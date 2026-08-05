import subprocess
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.core.evaluation import (
    canonical_ranking_score,
    evaluate_asset_candidates,
    refresh_candidate_snapshot,
)
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    MarketDataService,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import ResearchDataStore, ResearchDefinitionStore
from trading.research_data.result_schema import ResultValidity, ResultValidityStatus


class EvaluationCalendar:
    def __init__(self) -> None:
        self.sessions = pd.DatetimeIndex(pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"]))

    def latest_completed_session(self, _now):
        return date(2026, 8, 5)

    def sessions_in_range(self, start, end):
        return self.sessions[
            (self.sessions >= pd.Timestamp(start)) & (self.sessions <= pd.Timestamp(end))
        ]

    def session_on_or_before(self, value):
        return self.sessions[self.sessions <= pd.Timestamp(value)][-1].date()

    def session_on_or_after(self, value):
        return self.sessions[self.sessions >= pd.Timestamp(value)][0].date()

    def session_offset(self, value, offset):
        return self.sessions[self.sessions.get_loc(pd.Timestamp(value)) + offset].date()

    def session_distance(self, older, newer):
        return self.sessions.get_loc(pd.Timestamp(newer)) - self.sessions.get_loc(
            pd.Timestamp(older)
        )


class EvaluationProvider:
    def __init__(self, frame) -> None:
        self.frame = frame
        self.calls = []

    def fetch(self, _series, *, start, end):
        self.calls.append((start, end))
        return self.frame.loc[: pd.Timestamp(end)].copy()


def evaluation_bars() -> pd.DataFrame:
    close = pd.Series(
        [10.0, 11.0, 12.0],
        index=pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"]),
    )
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": 100.0,
        }
    )


def evaluation_definition(repository, blob_root):
    repository.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "baseline"],
        cwd=repository,
        check=True,
    )
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = repository / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    return ResearchDefinitionStore(blob_root).capture(
        resolved_config={"ticker": "SPY"},
        sources=sources,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
    )


def test_explicit_evaluation_refreshes_all_stale_candidates_before_ranking() -> None:
    statuses = {
        "spy_001": ResultValidity(ResultValidityStatus.DATA_STALE),
        "spy_002": ResultValidity(ResultValidityStatus.DEFINITION_STALE),
        "spy_003": ResultValidity(ResultValidityStatus.VALID),
    }
    refreshed: list[str] = []

    def refresh(name: str) -> None:
        refreshed.append(name)
        statuses[name] = ResultValidity(ResultValidityStatus.VALID)

    evaluation = evaluate_asset_candidates(
        "SPY",
        statuses,
        refresh=refresh,
        rank_key=lambda name: {"spy_001": 2.0, "spy_002": 3.0, "spy_003": 1.0}[name],
    )

    assert evaluation.complete
    assert refreshed == ["spy_001", "spy_002"]
    assert evaluation.ranking == ("spy_002", "spy_001", "spy_003")


def test_one_failed_refresh_prevents_a_complete_ranking_and_does_not_hide_other_errors() -> None:
    statuses = {
        "spy_001": ResultValidity(ResultValidityStatus.DATA_STALE),
        "spy_002": ResultValidity(ResultValidityStatus.DATA_STALE),
    }
    refreshed: list[str] = []

    def refresh(name: str) -> None:
        refreshed.append(name)
        if name == "spy_001":
            raise OSError("provider fake failed")
        statuses[name] = ResultValidity(ResultValidityStatus.VALID)

    evaluation = evaluate_asset_candidates("SPY", statuses, refresh=refresh)

    assert refreshed == ["spy_001", "spy_002"]
    assert evaluation.complete is False
    assert evaluation.ranking == ()
    assert any(
        "spy_001" in error and "provider fake failed" in error for error in evaluation.errors
    )


def test_legacy_and_unreproducible_candidates_cannot_be_qualified_by_refresh() -> None:
    statuses = {
        "spy_legacy": ResultValidity(ResultValidityStatus.LEGACY),
        "spy_broken": ResultValidity(ResultValidityStatus.UNREPRODUCIBLE),
    }
    refreshed: list[str] = []

    evaluation = evaluate_asset_candidates(
        "SPY",
        statuses,
        refresh=lambda name: refreshed.append(name),
    )

    assert refreshed == []
    assert evaluation.complete is False
    assert evaluation.ranking == ()
    assert any("legacy" in error for error in evaluation.errors)
    assert any("unreproducible" in error for error in evaluation.errors)


def test_candidate_ranking_uses_canonical_base_net_daily_equity_metrics() -> None:
    payload = {
        "part_b": {"sharpe_ratio": 99.0},
        "canonical_sleeve_evidence": {
            "scenarios": {
                "base_net": {"metrics": {"sharpe_ratio": 1.25}},
            }
        },
    }

    assert canonical_ranking_score(payload) == 1.25


def test_candidate_ranking_fails_closed_without_canonical_base_net_metrics() -> None:
    with pytest.raises(RuntimeError, match="canonical base-net"):
        canonical_ranking_score({"part_b": {"sharpe_ratio": 2.0}})


def test_explicit_refresh_publishes_a_new_current_snapshot_from_retained_requirements(
    tmp_path,
) -> None:
    calendar = EvaluationCalendar()
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        evaluation_bars().iloc[:2],
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    definition = evaluation_definition(tmp_path / "definition", tmp_path / "blobs")
    store = ResearchDataStore(tmp_path / "blobs")
    old_manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=definition.blob,
    )
    old_path = store.write_manifest(old_manifest, tmp_path / "old.snapshot.json")
    provider = EvaluationProvider(evaluation_bars())
    market_data = MarketDataService(
        provider=provider,
        cache=cache,
        calendar=calendar,
        now=lambda: datetime(2026, 8, 6, tzinfo=UTC),
    )

    new_path = refresh_candidate_snapshot(
        "spy_001",
        source_manifest_path=old_path,
        current_definition=definition,
        store=store,
        market_data_service=market_data,
        decision_session=date(2026, 8, 5),
        results_root=tmp_path / "results",
    )

    refreshed = store.load_manifest(new_path)
    assert refreshed.decision_time.session == date(2026, 8, 5)
    assert refreshed.definition == definition.blob
    assert provider.calls == [(None, date(2026, 8, 5))]

import subprocess
from dataclasses import replace
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import (
    ResearchDataStore,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunEvidenceError,
    RunMode,
)


def bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.0, 12.0],
            "Volume": [100.0, 200.0],
        },
        index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
    )


def deterministic_runner(series):
    def run(bundle):
        frame = bundle[series]
        return {
            "signals": [frame.index[-1].strftime("%Y-%m-%d")],
            "trades": [{"entry": float(frame.iloc[-1]["Close"])}],
            "metrics": {"last_close": float(frame.iloc[-1]["Close"])},
        }

    return run


def definition_blob(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "baseline"],
        cwd=tmp_path,
        check=True,
    )
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    return (
        ResearchDefinitionStore(tmp_path / "blobs")
        .capture(
            resolved_config={"ticker": "SPY"},
            sources=sources,
            execution_engine_version="execution-v1",
            dependency_versions={"pandas": "2.3.1"},
        )
        .blob
    )


def test_persisted_run_rejects_snapshot_without_definition_evidence(tmp_path) -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(
        tmp_path / "blobs",
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "data.snapshot.json")

    with pytest.raises(RunEvidenceError, match="definition evidence"):
        ResearchRunCoordinator(store=store, results_root=tmp_path / "results").execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            mode=RunMode.ONLINE,
        )

    assert not (tmp_path / "results").exists()


def test_online_offline_and_ephemeral_modes_have_distinct_publication_rules(tmp_path) -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(
        tmp_path / "blobs",
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=definition_blob(tmp_path),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "run.snapshot.json")
    coordinator = ResearchRunCoordinator(
        store=store,
        results_root=tmp_path / "results",
        now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
    )

    online = coordinator.execute(
        "experiment",
        deterministic_runner(series),
        manifest_path=manifest_path,
        current_definition=manifest.definition,
        mode=RunMode.ONLINE,
    )
    latest_path = tmp_path / "results" / "experiment" / "latest.json"
    latest_before_offline = latest_path.read_bytes()
    offline = coordinator.execute(
        "experiment",
        deterministic_runner(series),
        manifest_path=manifest_path,
        current_definition=manifest.definition,
        mode=RunMode.OFFLINE,
    )
    stale_online_coordinator = ResearchRunCoordinator(
        store=store,
        results_root=tmp_path / "stale-results",
        now=lambda: datetime(2026, 8, 6, 21, tzinfo=UTC),
    )
    with pytest.raises(RunEvidenceError, match="stale snapshot"):
        stale_online_coordinator.execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.ONLINE,
        )
    files_before_ephemeral = set((tmp_path / "results").rglob("*.json"))
    ephemeral = coordinator.execute(
        "experiment",
        deterministic_runner(series),
        manifest_path=manifest_path,
        mode=RunMode.EPHEMERAL,
    )

    assert latest_path.read_bytes() == latest_before_offline
    assert online.latest_path == latest_path
    assert online.persisted_path is not None
    assert offline.latest_path is None
    assert offline.persisted_path is not None
    assert ephemeral.latest_path is None
    assert ephemeral.persisted_path is None
    assert set((tmp_path / "results").rglob("*.json")) == files_before_ephemeral
    assert not (tmp_path / "stale-results").exists()
    for key in ("signals", "trades", "metrics"):
        assert online.result[key] == offline.result[key] == ephemeral.result[key]


def test_formal_run_rejects_current_definition_that_does_not_match_manifest(tmp_path) -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "blobs")
    definition = definition_blob(tmp_path)
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=definition,
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "run.snapshot.json")
    runner_called = False

    def runner(bundle):
        nonlocal runner_called
        runner_called = True
        return {"metrics": {}}

    with pytest.raises(RunEvidenceError, match="current research definition"):
        ResearchRunCoordinator(store=store, results_root=tmp_path / "results").execute(
            "experiment",
            runner,
            manifest_path=manifest_path,
            current_definition=replace(definition, fingerprint="0" * 64),
            mode=RunMode.OFFLINE,
        )

    assert runner_called is False
    assert not (tmp_path / "results").exists()

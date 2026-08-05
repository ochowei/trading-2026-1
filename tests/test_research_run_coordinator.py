import json
import subprocess
from dataclasses import replace
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.core.sleeve_engine import (
    CanonicalSleeveInput,
)
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import (
    ExperimentTrialRegistry,
    ResearchDataStore,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunEvidenceError,
    RunExecutionError,
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
        signal_date = frame.index[-1].date()
        sleeve_input = CanonicalSleeveInput(
            calendar=tuple(frame.index),
            close_prices=frame["Close"],
            candidates=(),
            raw_signals=(signal_date,),
            legacy_signals=(signal_date,),
            legacy_candidates=(),
            initial_capital=1.0,
        )
        return {
            "signals": [frame.index[-1].strftime("%Y-%m-%d")],
            "trades": [{"entry": float(frame.iloc[-1]["Close"])}],
            "metrics": {"last_close": float(frame.iloc[-1]["Close"])},
            "canonical_sleeve_input": sleeve_input,
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
            execution_engine_version="canonical-sleeve-v1",
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


def test_formal_run_requires_a_declared_experiment_family(tmp_path) -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "blobs")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=definition_blob(tmp_path),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "run.snapshot.json")

    with pytest.raises(RunEvidenceError, match="experiment family"):
        ResearchRunCoordinator(store=store, results_root=tmp_path / "results").execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.OFFLINE,
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
        experiment_family="test-family",
        now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
    )

    def non_normalized_runner(bundle):
        produced = deterministic_runner(series)(bundle)
        produced["canonical_sleeve_input"] = replace(
            produced["canonical_sleeve_input"],
            initial_capital=2.0,
        )
        return produced

    with pytest.raises(RunExecutionError, match="normalized initial capital 1.0"):
        coordinator.execute(
            "experiment",
            non_normalized_runner,
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.OFFLINE,
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
        experiment_family="test-family",
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
    assert online.result["schema_version"] == 3
    assert online.result["data_snapshot_id"] == manifest.snapshot_id
    assert online.result["definition_fingerprint"] == manifest.definition.fingerprint
    assert online.result["canonical_sleeve_evidence"]["raw_signals"] == ["2026-08-04"]
    assert (
        online.result["canonical_sleeve_evidence"]["cost_policies"]["base"]["entry_slippage_bps"]
        == 5.0
    )
    assert "canonical_sleeve_input" not in online.result
    assert json.loads(online.persisted_path.read_text())["validity"]["status"] == "valid"
    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    assert len(registry["trials"]) == 1
    assert len(registry["trials"][0]["observations"]) == 3
    assert offline.latest_path is None
    assert offline.persisted_path is not None
    assert ephemeral.latest_path is None
    assert ephemeral.persisted_path is None
    assert set((tmp_path / "results").rglob("*.json")) == files_before_ephemeral
    assert not (tmp_path / "stale-results").exists()
    for key in ("signals", "trades", "metrics"):
        assert online.result[key] == offline.result[key] == ephemeral.result[key]


def test_partial_formal_run_does_not_persist_a_result(tmp_path) -> None:
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

    with pytest.raises(RuntimeError, match="partial"):
        ResearchRunCoordinator(
            store=store,
            results_root=tmp_path / "results",
            experiment_family="test-family",
            now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
        ).execute(
            "experiment",
            lambda _bundle: {"partial": True, "part_a": {}},
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.ONLINE,
        )

    result_files = list((tmp_path / "results" / "experiment").glob("*.json"))
    assert result_files == []
    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    assert registry["trials"][0]["observations"][0]["outcome_status"] == "failed"


def test_failed_formal_runner_is_retained_as_trial_history_without_result_file(tmp_path) -> None:
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

    def failed_runner(_bundle):
        raise ValueError("synthetic failure")

    with pytest.raises(ValueError, match="synthetic failure"):
        ResearchRunCoordinator(
            store=store,
            results_root=tmp_path / "results",
            experiment_family="test-family",
            now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
        ).execute(
            "experiment",
            failed_runner,
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.ONLINE,
        )

    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    assert registry["trials"][0]["observations"][0]["outcome_status"] == "failed"
    assert not (tmp_path / "results" / "experiment" / "latest.json").exists()


def test_latest_publication_failure_is_retained_as_failed_trial_observation(
    tmp_path, monkeypatch
) -> None:
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
    from trading.research_data import runs as runs_module

    original_atomic_write = runs_module._atomic_write

    def fail_latest(path, content):
        if path.name == "latest.json":
            raise OSError("synthetic latest publication failure")
        return original_atomic_write(path, content)

    monkeypatch.setattr(runs_module, "_atomic_write", fail_latest)

    with pytest.raises(OSError, match="latest publication failure"):
        ResearchRunCoordinator(
            store=store,
            results_root=tmp_path / "results",
            experiment_family="test-family",
            now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
        ).execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.ONLINE,
        )

    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    observations = registry["trials"][0]["observations"]
    assert [item["outcome_status"] for item in observations] == ["succeeded", "failed"]
    assert observations[1]["observation_id"].endswith(":latest")
    assert not (tmp_path / "results" / "experiment" / "latest.json").exists()


def test_registry_failure_does_not_replace_existing_latest_result(tmp_path) -> None:
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
    latest = tmp_path / "results" / "experiment" / "latest.json"
    latest.parent.mkdir(parents=True)
    latest.write_bytes(b'{"previous": true}\n')
    previous = latest.read_bytes()

    class FailingObservationRegistry(ExperimentTrialRegistry):
        def record_observation(self, *args, **kwargs):
            raise RuntimeError("synthetic registry failure")

    with pytest.raises(RuntimeError, match="registry failure"):
        ResearchRunCoordinator(
            store=store,
            results_root=tmp_path / "results",
            experiment_family="test-family",
            trial_registry=FailingObservationRegistry(tmp_path / "results" / "trial_registry.json"),
            now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
        ).execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            current_definition=manifest.definition,
            mode=RunMode.ONLINE,
        )

    assert latest.read_bytes() == previous


def test_persisted_run_rejects_a_different_exact_definition_with_same_fingerprint(
    tmp_path,
) -> None:
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
    current_definition = replace(manifest.definition, digest="f" * 64)

    with pytest.raises(RunEvidenceError, match="exact research definition"):
        ResearchRunCoordinator(
            store=store,
            results_root=tmp_path / "results",
            now=lambda: datetime(2026, 8, 5, 13, tzinfo=UTC),
        ).execute(
            "experiment",
            deterministic_runner(series),
            manifest_path=manifest_path,
            current_definition=current_definition,
            mode=RunMode.OFFLINE,
        )


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

    with pytest.raises(RunEvidenceError, match="current exact research definition"):
        ResearchRunCoordinator(store=store, results_root=tmp_path / "results").execute(
            "experiment",
            runner,
            manifest_path=manifest_path,
            current_definition=replace(definition, fingerprint="0" * 64),
            mode=RunMode.OFFLINE,
        )

    assert runner_called is False
    assert not (tmp_path / "results").exists()

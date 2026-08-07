from __future__ import annotations

import json
from datetime import date

import pandas as pd

from trading.core.followup_cutover import (
    DataAccessParityOutputs,
    build_migration_parity_payload,
    run_verified_data_access_parity,
)
from trading.experiments.spy_007_trend_pullback.strategy import SPY007TrendPullbackStrategy
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataBundle,
    MarketDataRequirement,
    MarketDataSeries,
    PrimaryUSSessionCalendar,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import (
    MigrationParityStore,
    ResearchDataStore,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunMode,
)


def spy_bars() -> pd.DataFrame:
    sessions = PrimaryUSSessionCalendar().sessions_in_range(
        date(2010, 1, 1),
        date(2026, 3, 1),
    )
    close = pd.Series(100 + pd.RangeIndex(len(sessions)), index=sessions, dtype=float)
    return pd.DataFrame(
        {
            "Open": close - 0.25,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": 100.0,
        }
    )


def spy_bars_with_pullback_signals() -> pd.DataFrame:
    frame = spy_bars()
    for offset in (2350, 2850, 3350, 3800):
        timestamp = frame.index[offset]
        frame.loc[timestamp, "Low"] = frame.loc[timestamp, "Close"] - 20.0
    return frame


def test_spy_007_declares_one_primary_series_and_trial() -> None:
    strategy = SPY007TrendPullbackStrategy()

    requirements = strategy.market_data_requirements()
    assert len(requirements) == 1
    assert requirements[0] == MarketDataRequirement(
        MarketDataSeries.yahoo_adjusted_daily("SPY"),
        date(2010, 1, 1),
        role="primary",
    )

    trial = strategy.declare_experiment_trial()
    assert trial.family == "SPY:trend-pullback"
    assert "uptrend" in trial.hypothesis


def test_spy_007_definition_capture_includes_the_market_data_declaration(tmp_path) -> None:
    strategy = SPY007TrendPullbackStrategy()
    definition_store = ResearchDefinitionStore(tmp_path / "blobs")

    definition = strategy.capture_research_definition(definition_store)
    payload = definition_store.load(definition.blob)

    assert len(definition.fingerprint) == 64
    resolved_config = payload["resolved_config"]
    assert resolved_config["market_data_requirements"][0]["series"]["symbol"] == "SPY"
    assert resolved_config["market_data_requirements"][0]["role"] == "primary"


def test_spy_007_runner_consumes_only_the_declared_bundle(tmp_path) -> None:
    strategy = SPY007TrendPullbackStrategy()
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    frame = spy_bars()
    decision_time = SignalDecisionTime.for_primary_session(frame.index[-1].date())
    bundle = MarketDataBundle.from_requirements(
        (MarketDataRequirement(series, frame.index[0].date(), role="primary"),),
        {series: frame},
        decision_time=decision_time,
    )

    result = strategy.run_with_bundle(bundle)

    sleeve_input = result["canonical_sleeve_input"]
    assert sleeve_input.calendar == tuple(frame.index)
    assert sleeve_input.close_prices.equals(frame["Close"])
    assert sleeve_input.initial_capital == 1.0
    assert result["part_a"]["ticker"] == "SPY"
    assert result["part_b"]["ticker"] == "SPY"
    assert result["part_c"]["ticker"] == "SPY"


def test_spy_007_fixed_snapshot_parity_compares_legacy_and_migrated_paths(
    monkeypatch, tmp_path
) -> None:
    frame = spy_bars_with_pullback_signals()
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    bundle = MarketDataBundle.from_requirements(
        (MarketDataRequirement(series, frame.index[0].date(), role="primary"),),
        {series: frame},
        decision_time=SignalDecisionTime.for_primary_session(frame.index[-1].date()),
    )

    class RecordingDetector:
        def __init__(self, delegate):
            self.delegate = delegate
            self.indicators = None
            self.signal_frames = []

        def compute_indicators(self, source):
            self.indicators = self.delegate.compute_indicators(source)
            return self.indicators

        def detect_signals(self, source):
            result = self.delegate.detect_signals(source)
            self.signal_frames.append(result)
            return result

    class BundleDataFetcher:
        def __init__(self, **_kwargs):
            pass

        def fetch_all(self, tickers):
            return {
                ticker: bundle[MarketDataSeries.yahoo_adjusted_daily(ticker)] for ticker in tickers
            }

    def forbidden_provider(*_args, **_kwargs):
        raise AssertionError("fixed-snapshot parity must not contact a provider")

    monkeypatch.setattr("trading.core.base_strategy.DataFetcher", BundleDataFetcher)
    monkeypatch.setattr(
        "trading.market_data.provider.YahooFinanceProvider.fetch", forbidden_provider
    )
    legacy_strategy = SPY007TrendPullbackStrategy()
    legacy_detector = RecordingDetector(legacy_strategy.create_detector())
    legacy_strategy.create_detector = lambda: legacy_detector
    legacy_result = legacy_strategy.run()
    legacy_signals = tuple(
        item.date()
        for signal_frame in legacy_detector.signal_frames[:3]
        for item in signal_frame.index[signal_frame["Signal"]]
    )
    legacy_trades = tuple(
        trade
        for label in ("part_a", "part_b", "part_c")
        for trade in legacy_result[label]["trades"]
    )
    legacy_outputs = DataAccessParityOutputs(
        indicators=legacy_detector.indicators,
        signals=legacy_signals,
        trades=legacy_trades,
    )
    migrated_strategy = SPY007TrendPullbackStrategy()
    definition = migrated_strategy.capture_research_definition(
        ResearchDefinitionStore(tmp_path / "definition-blobs")
    )
    seen_bundles = []

    def load_snapshot(snapshot_id):
        assert snapshot_id == "a" * 64
        return bundle

    def legacy_runner(loaded_bundle):
        seen_bundles.append(loaded_bundle)
        return legacy_outputs

    def migrated_runner(loaded_bundle):
        seen_bundles.append(loaded_bundle)
        return migrated_strategy.run_for_parity(loaded_bundle)

    evidence = run_verified_data_access_parity(
        snapshot_id="a" * 64,
        detector_identity="spy_007_trend_pullback",
        result_fingerprint=definition.fingerprint,
        snapshot_loader=load_snapshot,
        legacy_runner=legacy_runner,
        migrated_runner=migrated_runner,
    )

    assert seen_bundles[0] is seen_bundles[1] is bundle
    assert evidence.result.passed is True
    assert evidence.result.differences == ()
    assert evidence.legacy_output_checksum == evidence.migrated_output_checksum
    assert legacy_outputs.signals
    assert legacy_outputs.trades

    payload = build_migration_parity_payload(
        evidence,
        experiment_name="spy_007_trend_pullback",
        legacy_definition="legacy:spy_007_trend_pullback",
        migrated_definition=definition.fingerprint,
        runtime={"python": "3.11", "dependencies": {"pandas": pd.__version__}},
    )
    path = MigrationParityStore.write(
        payload,
        tmp_path / "results" / "spy_007_trend_pullback" / (("a" * 64) + ".migration-parity.json"),
    )
    loaded = MigrationParityStore.load(path)
    assert loaded == payload
    assert loaded["passed"] is True
    assert loaded["outputs"]["legacy"]["layers"] == loaded["outputs"]["migrated"]["layers"]


def test_spy_007_runner_completes_an_offline_formal_execution(tmp_path) -> None:
    strategy = SPY007TrendPullbackStrategy()
    frame = spy_bars()
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        frame,
        refresh_kind=RefreshKind.FULL,
        refreshed_at=pd.Timestamp("2026-03-02", tz="UTC").to_pydatetime(),
    )
    definition_store = ResearchDefinitionStore(tmp_path / "blobs")
    definition = strategy.capture_research_definition(definition_store)
    store = ResearchDataStore(
        tmp_path / "blobs",
        now=lambda: pd.Timestamp("2026-03-02", tz="UTC").to_pydatetime(),
    )
    decision_time = SignalDecisionTime.for_primary_session(frame.index[-1].date())
    manifest = store.create_snapshot(
        cache,
        strategy.market_data_requirements(),
        decision_time,
        definition=definition.blob,
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "results" / "run.snapshot.json")

    outcome = ResearchRunCoordinator(
        store=store,
        results_root=tmp_path / "results",
        experiment_family=strategy.declare_experiment_trial().family,
        hypothesis=strategy.declare_experiment_trial().hypothesis,
    ).execute(
        "spy_007_trend_pullback",
        strategy.run_with_bundle,
        manifest_path=manifest_path,
        current_definition=definition.blob,
        mode=RunMode.OFFLINE,
    )

    assert outcome.persisted_path is not None
    assert outcome.latest_path is None
    assert outcome.result["schema_version"] == 3
    assert outcome.result["canonical_sleeve_evidence"]["engine_version"] == "canonical-sleeve-v1"
    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    assert registry["trials"][0]["experiment_family"] == "SPY:trend-pullback"
    assert registry["trials"][0]["definition_fingerprint"] == definition.fingerprint
    assert registry["trials"][0]["observations"][0]["run_mode"] == "offline"

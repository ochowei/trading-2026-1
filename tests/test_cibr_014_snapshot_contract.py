from __future__ import annotations

import json
from datetime import date

import pandas as pd

from trading.core.followup_cutover import DataAccessParityOutputs, run_verified_data_access_parity
from trading.experiments.cibr_014_multi_period_capitulation_mr.strategy import CIBR014Strategy
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
    ResearchDataStore,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunMode,
)


def cibr_bars() -> pd.DataFrame:
    sessions = PrimaryUSSessionCalendar().sessions_in_range(date(2018, 1, 1), date(2018, 5, 1))[:80]
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


def test_cibr_014_declares_one_primary_series_and_trial() -> None:
    strategy = CIBR014Strategy()

    requirements = strategy.market_data_requirements()
    assert requirements == (
        MarketDataRequirement(
            MarketDataSeries.yahoo_adjusted_daily("CIBR"),
            date(2018, 1, 1),
            role="primary",
        ),
    )
    trial = strategy.declare_experiment_trial()
    assert trial.family == "CIBR:capitulation-mr"
    assert "ATR" in trial.hypothesis


def test_cibr_014_runner_consumes_only_the_declared_bundle() -> None:
    strategy = CIBR014Strategy()
    frame = cibr_bars()
    series = MarketDataSeries.yahoo_adjusted_daily("CIBR")
    bundle = MarketDataBundle.from_requirements(
        strategy.market_data_requirements(),
        {series: frame},
        decision_time=SignalDecisionTime.for_primary_session(frame.index[-1].date()),
    )

    result = strategy.run_with_bundle(bundle)

    assert result["canonical_sleeve_input"].calendar == tuple(frame.index)
    assert result["canonical_sleeve_input"].close_prices.equals(frame["Close"])
    assert result["part_a"]["backtest_period"]["start"] == strategy.create_config().part_a_start
    assert result["part_b"]["trades"] == []


def test_cibr_014_fixed_bundle_parity_never_needs_a_provider(monkeypatch) -> None:
    strategy = CIBR014Strategy()
    frame = cibr_bars()
    series = MarketDataSeries.yahoo_adjusted_daily("CIBR")
    bundle = MarketDataBundle.from_requirements(
        strategy.market_data_requirements(),
        {series: frame},
        decision_time=SignalDecisionTime.for_primary_session(frame.index[-1].date()),
    )
    migrated_outputs = strategy.run_for_parity(bundle)

    class BundleDataFetcher:
        def __init__(self, **_kwargs):
            pass

        def fetch_all(self, tickers):
            return {
                ticker: bundle[MarketDataSeries.yahoo_adjusted_daily(ticker)] for ticker in tickers
            }

    monkeypatch.setattr("trading.core.base_strategy.DataFetcher", BundleDataFetcher)
    monkeypatch.setattr(
        "trading.market_data.provider.YahooFinanceProvider.fetch",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("fixed-snapshot parity must not contact a provider")
        ),
    )
    legacy = CIBR014Strategy()
    legacy_outputs = _legacy_outputs(legacy)

    evidence = run_verified_data_access_parity(
        snapshot_id="a" * 64,
        detector_identity="cibr_014_multi_period_capitulation_mr",
        result_fingerprint="b" * 64,
        snapshot_loader=lambda _snapshot_id: bundle,
        legacy_runner=lambda _bundle: legacy_outputs,
        migrated_runner=lambda _bundle: migrated_outputs,
    )

    assert evidence.result.passed is True
    assert evidence.legacy_output_checksum == evidence.migrated_output_checksum


def test_cibr_014_runner_completes_an_offline_formal_execution(tmp_path) -> None:
    strategy = CIBR014Strategy()
    frame = cibr_bars()
    series = MarketDataSeries.yahoo_adjusted_daily("CIBR")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    refreshed_at = pd.Timestamp("2018-05-02", tz="UTC").to_pydatetime()
    cache.publish(series, frame, refresh_kind=RefreshKind.FULL, refreshed_at=refreshed_at)

    definition_store = ResearchDefinitionStore(tmp_path / "blobs")
    definition = strategy.capture_research_definition(definition_store)
    store = ResearchDataStore(tmp_path / "blobs", now=lambda: refreshed_at)
    decision_time = SignalDecisionTime.for_primary_session(frame.index[-1].date())
    manifest = store.create_snapshot(
        cache,
        strategy.market_data_requirements(),
        decision_time,
        definition=definition.blob,
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "results" / "run.snapshot.json")
    trial = strategy.declare_experiment_trial()

    outcome = ResearchRunCoordinator(
        store=store,
        results_root=tmp_path / "results",
        experiment_family=trial.family,
        hypothesis=trial.hypothesis,
        now=lambda: refreshed_at,
    ).execute(
        "cibr_014_multi_period_capitulation_mr",
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
    assert registry["trials"][0]["experiment_family"] == "CIBR:capitulation-mr"
    assert registry["trials"][0]["definition_fingerprint"] == definition.fingerprint
    assert registry["trials"][0]["observations"][0]["run_mode"] == "offline"


def _legacy_outputs(strategy: CIBR014Strategy) -> DataAccessParityOutputs:
    original_detector = strategy.create_detector()

    class RecordingDetector:
        def __init__(self):
            self.indicators = None
            self.signal_frames = []

        def compute_indicators(self, source):
            self.indicators = original_detector.compute_indicators(source)
            return self.indicators

        def detect_signals(self, source):
            result = original_detector.detect_signals(source)
            self.signal_frames.append(result)
            return result

    recording = RecordingDetector()
    strategy.create_detector = lambda: recording
    result = strategy.run()
    signals = tuple(
        item.date() for frame in recording.signal_frames for item in frame.index[frame["Signal"]]
    )
    trades = tuple(
        trade for label in ("part_a", "part_b", "part_c") for trade in result[label]["trades"]
    )
    return DataAccessParityOutputs(recording.indicators, signals, trades)

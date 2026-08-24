from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from trading.experiments.spy_007_trend_pullback.strategy import SPY007TrendPullbackStrategy
from trading.experiments.spy_010_trend_pullback_baseline.config import create_default_config
from trading.experiments.spy_010_trend_pullback_baseline.signal_detector import (
    SPY010TrendPullbackBaselineDetector,
)
from trading.experiments.spy_010_trend_pullback_baseline.strategy import (
    SPY010TrendPullbackBaselineStrategy,
)
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataBundle,
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

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RETAINED_ONLINE_RESULT = Path(
    "results/spy_010_trend_pullback_baseline/"
    "20260810_094817_641071_online_24af2275c923454f8d7b332920a4033a.json"
)


def _spy_bars() -> pd.DataFrame:
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


def test_spy_010_registry_observation_result_is_retained_and_not_ignored() -> None:
    historical = REPOSITORY_ROOT / RETAINED_ONLINE_RESULT
    latest = REPOSITORY_ROOT / "results/spy_010_trend_pullback_baseline/latest.json"

    assert historical.read_bytes() == latest.read_bytes()
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", RETAINED_ONLINE_RESULT.as_posix()],
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    assert ignored.returncode == 1


def test_spy_010_freezes_attempt_2_parameters_and_family() -> None:
    config = create_default_config()
    strategy = SPY010TrendPullbackBaselineStrategy()

    assert config.experiment_id == "SPY-010"
    assert config.cooldown_days == 10
    assert config.profit_target == 0.03
    assert config.stop_loss == -0.03
    assert config.holding_days == 20
    trial = strategy.declare_experiment_trial()
    assert trial.family == "SPY:trend-pullback"
    assert "baseline" in trial.hypothesis
    assert "without ClosePos" in trial.hypothesis


def test_spy_010_detector_has_no_close_position_gate_and_uses_ten_session_cooldown() -> None:
    index = pd.bdate_range("2026-01-02", periods=12)
    frame = pd.DataFrame(
        {
            "Close": 110.0,
            "Low": 106.0,
            "SMA_Short": 105.0,
            "SMA_Mid": 102.0,
            "SMA_Long": 100.0,
        },
        index=index,
    )
    frame.loc[index[[0, 10, 11]], "Low"] = 104.0

    signaled = SPY010TrendPullbackBaselineDetector(create_default_config()).detect_signals(frame)

    assert "ClosePos" not in signaled
    assert signaled.index[signaled["Signal"]].tolist() == [index[0], index[11]]


def test_spy_010_definition_is_distinct_from_selected_trial(tmp_path) -> None:
    store = ResearchDefinitionStore(tmp_path / "blobs")
    baseline = SPY010TrendPullbackBaselineStrategy().capture_research_definition(store)
    selected = SPY007TrendPullbackStrategy().capture_research_definition(store)

    assert baseline.fingerprint != selected.fingerprint
    payload = store.load(baseline.blob)
    assert payload["resolved_config"]["config"]["name"] == "spy_010_trend_pullback_baseline"
    assert payload["resolved_config"]["market_data_requirements"][0]["role"] == "primary"


def test_spy_010_runner_consumes_declared_bundle_and_builds_canonical_sleeve() -> None:
    strategy = SPY010TrendPullbackBaselineStrategy()
    frame = _spy_bars()
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    bundle = MarketDataBundle.from_requirements(
        strategy.market_data_requirements(),
        {series: frame},
        decision_time=SignalDecisionTime.for_primary_session(frame.index[-1].date()),
    )

    result = strategy.run_with_bundle(bundle)

    sleeve = result["canonical_sleeve_input"]
    assert sleeve.calendar == tuple(frame.index)
    assert sleeve.close_prices.equals(frame["Close"])
    assert sleeve.initial_capital == 1.0
    assert result["metadata"]["experiment"] == "spy_010_trend_pullback_baseline"


def test_spy_010_offline_execution_registers_a_distinct_family_trial(tmp_path) -> None:
    strategy = SPY010TrendPullbackBaselineStrategy()
    frame = _spy_bars()
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
        "spy_010_trend_pullback_baseline",
        strategy.run_with_bundle,
        manifest_path=manifest_path,
        current_definition=definition.blob,
        mode=RunMode.OFFLINE,
    )

    assert outcome.persisted_path is not None
    assert outcome.latest_path is None
    registry = json.loads((tmp_path / "results" / "trial_registry.json").read_text())
    assert registry["trials"][0]["experiment_family"] == "SPY:trend-pullback"
    assert registry["trials"][0]["definition_fingerprint"] == definition.fingerprint
    assert registry["trials"][0]["observations"][0]["run_mode"] == "offline"

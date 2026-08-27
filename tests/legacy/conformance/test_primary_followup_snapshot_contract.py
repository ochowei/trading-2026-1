from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from trading.core.bundle_strategy import PrimaryBundleStrategyMixin
from trading.experiments import get_experiment
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

pytestmark = pytest.mark.legacy_conformance

PRIMARY_FOLLOWUP_EXPERIMENTS = (
    "cibr_001_pullback_wr",
    "cibr_002_vol_adaptive_mr",
    "cibr_003_bb_squeeze_breakout",
    "cibr_004_rsi2_vol_adaptive",
    "cibr_005_20d_lookback_mr",
    "copx_001_pullback_wr",
    "copx_002_deep_drawdown",
    "copx_003_exit_optimized",
    "copx_005_bb_squeeze_breakout",
    "copx_006_pairs_fcx",
    "copx_007_vol_adaptive",
    "copx_008_rs_momentum",
    "copx_009_rsi_divergence_mr",
    "copx_010_vol_transition_mr",
    "copx_011_regime_breakout",
    "copx_012_atr_ceiling_mr",
    "copx_018_volume_confirmed_mr",
    "cibr_007_bb_lower_mr",
    "cibr_008_bb_lower_pullback_cap",
    "cibr_009_key_reversal_day_mr",
    "cibr_010_nr7_pullback_mr",
    "cibr_011_range_expansion_mr",
    "cibr_012_vol_transition_mr",
    "cibr_013_higher_low_confirmation_mr",
    "cibr_015_momentum_pullback",
    "cibr_016_vol_level_gate_mr",
    "dia_001_pullback_wr_reversal",
    "dia_002_rsi2_reversal",
    "dia_003_rsi2_bb",
    "dia_004_wider_tp",
    "dia_005_extreme_entry",
    "dia_006_bb_squeeze_breakout",
    "dia_007_trend_pullback",
    "dia_008_momentum_pullback",
    "dia_010_rsi5_trend_pullback",
    "dia_011_vol_adaptive_rsi2",
    "dia_012_oneday_capitulation_filter",
    "dia_017_trend_regime_gate_mr",
    "dia_013_trend_regime_pullback",
    "ewj_001_pullback_wr_reversal",
    "ewj_003_bb_lower_mr",
    "ewj_005_vol_transition_mr",
    "eem_001_rsi2_mean_reversion",
    "eem_002_vol_adaptive_rsi2",
    "eem_003_vol_adaptive_deep_decline",
    "eem_004_pullback_wr",
    "eem_005_bb_squeeze_breakout",
    "eem_007_trend_momentum_pullback",
    "eem_008_optimized_breakout",
    "eem_009_atr_sl_rsi2",
    "eem_010_strict_decline_atr",
    "eem_011_no_closepos_atr",
    "eem_012_bb_lower_pullback_cap",
    "eem_013_macd_histogram_mr",
    "eem_014_vol_transition_mr",
    "eem_015_multi_period_cap",
    "eem_021_bb_width_regime_gate_mr",
    "ewt_002_vol_adaptive_pullback",
    "ewt_003_bb_squeeze_breakout",
    "ewt_004_crash_filter_asymmetric",
    "ewt_005_rsi2_vol_adaptive",
    "ewt_006_optimized_exit_mr",
    "ewt_008_bb_lower_pullback_cap",
    "ewt_009_vol_transition_mr",
    "ewj_002_vol_adaptive_pullback",
    "ewt_001_pullback_wr_reversal",
    "ewz_006_bb_lower_pullback_cap",
    "ewz_001_pullback_wr",
    "ewz_002_vol_adaptive_pullback",
    "ewz_003_bb_squeeze_breakout",
    "ewz_004_trend_momentum_pullback",
    "ewz_007_vol_transition_mr",
    "fcx_001_extreme_oversold",
    "fcx_002_pullback_wr",
    "fcx_003_optimized_exit",
    "fcx_004_bb_squeeze_breakout",
    "fcx_005_momentum_pullback",
    "fcx_007_donchian_breakout",
    "fcx_009_rsi_divergence_mr",
    "fcx_010_gap_reversal_mr",
    "fcx_011_vol_transition_mr",
    "fcx_012_donchian_low_washout",
    "fcx_013_regime_breakout",
    "fcx_014_breakout_ceiling",
    "fxi_001_pullback_wr",
    "fxi_002_vol_adaptive_pullback",
    "fxi_003_bb_squeeze_breakout",
    "fxi_004_rsi5_2d_decline",
    "fxi_006_bb_lower_mr",
    "fxi_008_stochastic_mr",
    "fxi_009_failed_breakdown_reversal",
    "fxi_010_gap_reversal_mr",
    "fxi_011_connors_rsi_mr",
    "fxi_012_momentum_pullback",
    "fxi_013_regime_vol_gate_mr",
    "fxi_014_atr_band_mr",
    "gld_001_mean_reversion",
    "gld_002_optimized_exit",
    "gld_003_trailing_stop",
    "gld_004_bollinger_reversion",
    "gld_005_keltner_reversion",
    "gld_006_pullback_wr",
    "gld_007_pullback_wr_reversal",
    "gld_008_rsi2_trailing",
    "gld_009_bb_squeeze_breakout",
    "gld_010_momentum_pullback",
    "gld_011_donchian_breakout",
    "gld_012_atr_adaptive",
    "gld_013_vol_transition_mr",
    "gld_014_capitulation_filter",
    "inda_001_pullback_wr_reversal",
    "inda_002_vol_adaptive_mr",
    "inda_003_bb_squeeze_breakout",
    "inda_004_rsi2_atr_adaptive",
    "inda_005_crash_filtered_mr",
    "inda_006_exit_optimized_mr",
    "inda_008_bb_lower_pullback_cap",
    "inda_009_cci_oversold_mr",
    "inda_011_multi_period_capitulation",
    "ibit_001_pullback_wr",
    "ibit_002_rsi2_pullback",
    "ibit_003_bb_squeeze_breakout",
    "ibit_004_vol_adaptive",
    "ibit_005_extended_lookback",
    "ibit_006_gap_reversal_mr",
    "ibit_007_keltner_lower_mr",
    "ibit_008_range_expansion_mr",
    "ibit_009_post_cap_vol_transition_mr",
    "fcx_008_trend_pullback",
    "fxi_005_wr14_extended_mr",
    "inda_010_vol_transition_mr",
    "iwm_001_rsi2_reversal",
    "iwm_002_pullback_wr",
    "iwm_003_rsi2_optimized",
    "iwm_004_relative_weakness",
    "iwm_005_shorter_hold",
    "iwm_006_bb_squeeze_breakout",
    "iwm_007_trend_pullback",
    "iwm_008_bb_squeeze_optimized",
    "iwm_010_pullback_rsi2_hybrid",
    "iwm_011_vol_adaptive_rsi2",
    "iwm_012_bb_lower_pullback_cap",
    "iwm_013_capitulation_filter",
    "iwm_014_momentum_pullback",
    "nvda_001_extreme_oversold",
    "nvda_002_capped_drawdown",
    "nvda_003_bb_squeeze_breakout",
    "nvda_004_bb_squeeze_optimized",
    "nvda_005_momentum_pullback",
    "nvda_009_momentum_pullback",
    "nvda_010_adx_rsi2_mr",
    "nvda_011_capitulation_filter",
    "nvda_012_regime_breakout",
    "nvda_013_regime_mbpc",
    "nvda_017_signal_day_filter",
    "nvda_019_failed_breakdown_mr",
    "nvda_020_atr_band_mbpc",
    "sivr_006_closepos_pullback_wr",
    "sivr_001_mean_reversion",
    "sivr_002_trailing_stop",
    "sivr_003_pullback_wr",
    "sivr_004_rsi2_pullback",
    "sivr_005_capped_pullback_wr",
    "sivr_007_divergence_pullback_wr",
    "sivr_008_bb_squeeze_breakout",
    "sivr_010_rs_momentum",
    "sivr_011_sharp_decline_rsi5",
    "sivr_012_vol_adaptive_mr",
    "sivr_013_bb_lower_mr",
    "sivr_014_donchian_breakout",
    "sivr_015_rsi_divergence_mr",
    "sivr_016_wvf_capitulation_mr",
    "sivr_017_mfi_capitulation_mr",
    "sivr_018_atr_band_mr",
    "soxl_001_extreme_oversold",
    "soxl_002_deep_oversold",
    "soxl_003_wide_sl",
    "soxl_004_reversal_confirm",
    "soxl_005_capped_drawdown",
    "soxl_006_selective_oversold",
    "soxl_008_wr_oscillator",
    "soxl_009_bb_squeeze_breakout",
    "soxl_012_regime_vol_gate",
    "soxl_013_signal_day_capitulation_cap",
    "spy_001_pullback_wr",
    "spy_002_no_trailing",
    "spy_004_rsi2_reversal",
    "spy_005_asymmetric_exit",
    "spy_006_roc_reversal",
    "spy_008_bb_squeeze_breakout",
    "spy_009_capitulation_filter",
    "tsla_001_extreme_oversold",
    "tsla_002_wider_exit",
    "tsla_003_tight_retracement",
    "tsla_004_wr_reversion",
    "tsla_005_bb_squeeze_breakout",
    "tsla_006_trend_pullback",
    "tsla_007_keltner_breakout",
    "tsla_008_rs_momentum_pullback",
    "tsla_009_bb_wide_breakout",
    "tsla_010_rsi5_mean_reversion",
    "tsla_011_momentum_recovery",
    "tsla_012_volume_breakout",
    "tsla_013_pre_breakout_calm",
    "tsla_014_vol_transition_mr",
    "tsla_015_regime_breakout",
    "tsla_016_breakout_ceiling",
    "tsm_001_extreme_oversold",
    "tsm_002_pullback_wr_reversal",
    "tsm_003_rsi2_reversal",
    "tsm_004_smh_confirm",
    "tsm_005_bb_squeeze_breakout",
    "tsm_006_momentum_pullback",
    "tsm_010_regime_mbpc",
    "ura_001_pullback_wr",
    "ura_002_asymmetric_narrow",
    "ura_004_20d_pullback_rsi2",
    "ura_005_bb_squeeze_breakout",
    "ura_007_vol_adaptive",
    "ura_008_rsi_divergence_mr",
    "ura_009_day_after_reversal_mr",
    "ura_010_wvf_capitulation_mr",
    "ura_011_volume_capitulation_mr",
    "ura_012_atr_band_mr",
    "ura_013_multi_period_cap_mr",
    "ura_014_postparabola_regime_mr",
    "tlt_001_pullback_wr_reversal",
    "tlt_002_deep_pullback_lower_tp",
    "tlt_003_wide_asymmetric",
    "tlt_004_bb_squeeze_breakout",
    "tlt_005_donchian_momentum",
    "tlt_006_day_after_reversal_mr",
    "tlt_007_regime_vol_gate_mr",
    "tlt_010_capitulation_regime_mr",
    "tlt_011_dynamic_regime_mr",
    "tlt_012_sustained_regime_mr",
    "xlu_001_pullback_wr_reversal",
    "xlu_003_tight_pullback_wr",
    "xlu_004_bb_squeeze_breakout",
    "xlu_008_tight_squeeze_breakout",
    "xlu_009_kc_squeeze_breakout",
    "xlu_010_20d_wide_pullback",
    "xlu_011_vol_adaptive_mr",
    "xlu_012_vol_transition_mr",
    "vgk_001_rsi2_mean_reversion",
    "vgk_002_vol_adaptive_pullback",
    "vgk_002_vol_adaptive_rsi2",
    "vgk_003_pullback_wr",
    "vgk_004_crash_isolated_mr",
    "vgk_005_decline_enhanced_mr",
    "vgk_006_trend_pullback_momentum",
    "vgk_008_vol_transition_mr",
    "ura_003_pullback_rsi2",
    "uso_001_pullback_wr",
    "uso_005_symmetric_tight",
    "uso_007_sharp_pullback",
    "uso_009_momentum_pullback",
    "uso_010_deep_pullback",
    "uso_012_capped_pullback",
    "uso_013_tight_cap",
    "uso_021_bb_squeeze_breakout",
    "uso_022_rsi_divergence_mr",
    "uso_023_vol_adaptive_mr",
    "uso_024_regime_breakout",
    "uso_029_trend_pullback_continuation",
    "vgk_007_bb_lower_mr",
    "voo_001_rsi2_reversal",
    "voo_002_asymmetric_exit",
    "voo_003_wider_tp",
    "voo_004_momentum_pullback",
    "voo_005_capitulation_filter",
    "voo_006_signal_day_capitulation_mr",
    "xbi_001_pullback_wr",
    "xbi_004_capped_cooldown",
    "xbi_005_closepos_reversal",
    "xbi_006_bb_squeeze_breakout",
    "xbi_007_momentum_pullback",
    "xbi_009_vol_adaptive",
    "xbi_010_bb_lower_pullback_cap",
    "xbi_011_rsi_divergence_mr",
    "xbi_012_capitulation_accel",
    "xbi_013_gap_reversal_mr",
    "xbi_014_vol_transition_mr",
    "xbi_015_regime_pullback_mr",
    "xlu_002_capped_pullback_wr",
)

PRIMARY_SMOKE_EXPERIMENTS = frozenset(
    {
        "cibr_001_pullback_wr",
        "cibr_003_bb_squeeze_breakout",
        "copx_006_pairs_fcx",
        "eem_013_macd_histogram_mr",
        "ibit_006_gap_reversal_mr",
        "nvda_010_adx_rsi2_mr",
        "soxl_009_bb_squeeze_breakout",
        "tlt_007_regime_vol_gate_mr",
        "tsla_007_keltner_breakout",
        "xlu_009_kc_squeeze_breakout",
    }
)


def _experiment_case(experiment_name: str) -> pytest.ParameterSet:
    marker = (
        pytest.mark.legacy_smoke
        if experiment_name in PRIMARY_SMOKE_EXPERIMENTS
        else pytest.mark.slow
    )
    return pytest.param(experiment_name, marks=marker)


PRIMARY_FOLLOWUP_CASES = tuple(
    _experiment_case(experiment_name) for experiment_name in PRIMARY_FOLLOWUP_EXPERIMENTS
)


@pytest.fixture(scope="module")
def primary_bars() -> pd.DataFrame:
    sessions = PrimaryUSSessionCalendar().sessions_in_range(date(2010, 1, 1), date(2025, 1, 7))
    close = pd.Series(100.0 + pd.RangeIndex(len(sessions)), index=sessions)
    return pd.DataFrame(
        {
            "Open": close - 0.25,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": 100_000.0,
        }
    )


@pytest.mark.parametrize("experiment_name", PRIMARY_FOLLOWUP_CASES)
def test_primary_followup_uses_declared_primary_bundle(
    experiment_name: str,
    primary_bars: pd.DataFrame,
    monkeypatch,
) -> None:
    strategy = get_experiment(experiment_name)
    assert isinstance(strategy, PrimaryBundleStrategyMixin)

    requirements = strategy.market_data_requirements()
    assert len(requirements) == 1
    assert requirements[0].role == "primary"
    series = requirements[0].series
    assert series == MarketDataSeries.yahoo_adjusted_daily(strategy.create_config().tickers[0])
    bundle = MarketDataBundle.from_requirements(
        requirements,
        {series: primary_bars},
        decision_time=SignalDecisionTime.for_primary_session(primary_bars.index[-1].date()),
    )

    monkeypatch.setattr(
        "trading.market_data.provider.YahooFinanceProvider.fetch",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("primary bundle execution must not contact a provider")
        ),
    )
    result = strategy.run_with_bundle(bundle)
    trial = strategy.declare_experiment_trial()

    assert trial.family
    assert result["canonical_sleeve_input"].calendar == tuple(primary_bars.index)
    assert result["canonical_sleeve_input"].close_prices.equals(primary_bars["Close"])
    assert result["metadata"]["experiment"] == experiment_name


@pytest.mark.legacy_smoke
def test_primary_followup_definition_capture_includes_shared_bundle_executor(tmp_path) -> None:
    strategy = get_experiment("copx_007_vol_adaptive")
    definition_store = ResearchDefinitionStore(tmp_path / "blobs")
    definition = strategy.capture_research_definition(definition_store)
    payload = definition_store.load(definition.blob)
    assert definition.fingerprint
    assert "bundle_executor" in payload["sources"]


@pytest.mark.parametrize("experiment_name", PRIMARY_FOLLOWUP_CASES)
def test_primary_followup_completes_formal_offline_execution(
    experiment_name: str,
    primary_bars: pd.DataFrame,
    tmp_path,
) -> None:
    strategy = get_experiment(experiment_name)
    series = strategy.market_data_requirements()[0].series
    refreshed_at = pd.Timestamp("2020-01-08", tz="UTC").to_pydatetime()
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(series, primary_bars, refresh_kind=RefreshKind.FULL, refreshed_at=refreshed_at)
    definition_store = ResearchDefinitionStore(tmp_path / "blobs")
    definition = strategy.capture_research_definition(definition_store)
    store = ResearchDataStore(tmp_path / "blobs", now=lambda: refreshed_at)
    manifest = store.create_snapshot(
        cache,
        strategy.market_data_requirements(),
        SignalDecisionTime.for_primary_session(primary_bars.index[-1].date()),
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
        experiment_name,
        strategy.run_with_bundle,
        manifest_path=manifest_path,
        current_definition=definition.blob,
        mode=RunMode.OFFLINE,
    )

    assert outcome.persisted_path is not None
    assert outcome.latest_path is None
    assert outcome.result["schema_version"] == 3

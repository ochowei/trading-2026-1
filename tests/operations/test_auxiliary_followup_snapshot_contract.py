from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.experiments import get_experiment
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataBundle,
    MarketDataCoveragePolicy,
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

AUXILIARY_FOLLOWUP_EXPERIMENTS = (
    "cibr_006_rs_momentum_pullback",
    "cibr_017_vix_bands_mr",
    "copx_013_macro_confirmed_mr",
    "copx_014_gld_divergence_breakout",
    "copx_015_vix_bands_breakout",
    "copx_016_dxy_direction_breakout",
    "copx_017_yield_curve_slope_mr",
    "copx_019_copper_direction_mr",
    "eem_006_rs_momentum_pullback",
    "eem_016_dxy_direction_mr",
    "eem_017_eem_efa_divergence_mr",
    "eem_018_vix_bands_mr",
    "eem_019_eem_fxi_divergence_mr",
    "eem_020_multi_anchor_combo_mr",
    "eem_022_global_macro_context_mr",
    "ewt_007_rs_momentum",
    "ewt_010_ewt_eem_2d_divergence_mr",
    "ewt_011_vol_gated_rs_momentum",
    "ewt_012_eem_divergence_regime_mr",
    "ewz_005_rs_momentum",
    "ewz_008_vix_implied_vol_mr",
    "ewz_009_ewz_eem_divergence_mr",
    "ewz_010_brl_regime_mr",
    "ewj_004_rs_momentum",
    "ewj_006_usdjpy_direction_mr",
    "ewj_007_vix_implied_vol_mr",
    "dia_009_pairs_spy",
    "dia_014_iwm_divergence_mr",
    "dia_015_vix_direction_mr",
    "dia_016_qqq_divergence_mr",
    "dia_018_vix_bands_mr",
    "dia_019_qqq_macro_confirm_mr",
    "iwm_009_momentum_rotation",
    "iwm_015_macro_confirmed_mr",
    "tlt_008_duration_spread_mr",
    "tlt_009_yield_velocity_mr",
    "tlt_013_move_implied_vol_mr",
    "tlt_014_tlt_spy_divergence_mr",
    "tlt_015_hyg_credit_divergence_mr",
    "tlt_016_move_multi_window_direction_mr",
    "fcx_006_relative_strength",
    "fcx_015_vix_bands_breakout",
    "fcx_016_postparabola_regime_breakout",
    "fxi_007_rs_momentum",
    "fxi_015_ashr_divergence_mr",
    "fxi_016_usdcnh_direction_mr",
    "fxi_017_cny_regime_mr",
    "inda_007_rs_momentum",
    "inda_012_inda_eem_rs60d_divergence_mr",
    "inda_013_broad_em_confirmed_mr",
    "inda_014_dxy_direction_mr",
    "inda_015_implied_vol_regime_mr",
    "gld_015_gvz_implied_vol_mr",
    "gld_016_dxy_divergence_mr",
    "gld_017_usd_regime_mr",
    "nvda_006_relative_strength",
    "nvda_007_rs_exit_optimized",
    "nvda_008_rs_param_explore",
    "nvda_014_negative_rs_mr",
    "nvda_015_regime_rs",
    "nvda_016_sector_confirmed_mbpc",
    "nvda_018_vxn_implied_vol_mbpc",
    "nvda_021_qqq_divergence_mbpc",
    "spy_003_optimized_wr",
    "soxl_010_sector_rs_momentum",
    "soxl_011_soxx_atr_adaptive",
    "tlt_017_yield_curve_slope_mr",
    "tqqq_004_cap_vix_filter",
    "tqqq_005_cap_vix_adaptive",
    "tqqq_007_cap_qqq_confirm",
    "tqqq_012_cap_exec_qqq_confirm",
    "tqqq_014_cap_exec_vix_adaptive",
    "tqqq_015_qqq_trend_breakout",
    "tqqq_025_vxn_vix_vvix_filter",
    "tqqq_019_vix_direction_mr",
    "tqqq_020_vix_peak_passing_mr",
    "tqqq_021_move_regime_gate",
    "tqqq_022_qqq_spy_divergence_cap",
    "tqqq_023_yield_curve_slope_cap",
    "tqqq_026_sqqq_pair_divergence",
    "tqqq_027_qqq_single_day_reversal",
    "xbi_008_pairs_ibb",
    "xbi_016_macro_confirmed_mr",
    "xbi_017_vix_bands_mr",
    "xbi_019_xlv_trend_mr",
    "xbi_020_vix_direction_mr",
    "xlu_013_move_implied_vol_mr",
    "xlu_014_tnx_rate_direction_mr",
    "xlu_005_trend_pullback",
    "xlu_006_rsi2_wide_sl",
    "xlu_007_momentum_pullback",
    "sivr_009_ratio_reversion",
    "sivr_019_gvz_direction_mr",
    "sivr_020_usd_regime_mr",
    "uso_025_ovx_implied_vol_mr",
    "uso_026_xle_divergence_mr",
    "uso_027_multi_period_cap_mr",
    "uso_028_ovx_5d_direction_mr",
    "tsla_017_qqq_divergence_breakout",
    "tsla_018_dxy_direction_breakout",
    "tsla_019_vix_bands_breakout",
    "tsla_020_usd_regime_breakout",
    "tsm_007_relative_strength",
    "tsm_008_rs_exit_optimization",
    "tsm_009_pairs_trading",
    "tsm_011_signal_day_filter",
    "tsm_012_volume_confirmed_rs_pullback",
    "tsm_013_qqq_divergence_rs",
    "tsm_014_qqq_divergence_band",
    "tsm_015_aapl_divergence_rs",
    "tsm_016_bb_width_regime_gate",
    "tsm_017_earnings_exclusion",
    "tsm_018_atr_band_rs",
    "tsm_019_vix_term_structure_rs",
    "tsm_020_soxx_divergence_rs",
    "tsm_021_qqq_macro_health_gate",
    "tsm_022_vxn_implied_vol_rs",
    "ura_006_trend_pullback",
    "vgk_009_eurusd_direction_mr",
    "xbi_018_xbi_xlv_divergence_mr",
)


@pytest.fixture(scope="module")
def historical_bars() -> pd.DataFrame:
    sessions = PrimaryUSSessionCalendar().sessions_in_range(date(2009, 1, 1), date(2020, 1, 6))
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


def _bundle(strategy, frame: pd.DataFrame) -> MarketDataBundle:
    requirements = strategy.market_data_requirements()
    frames = {requirement.series: frame for requirement in requirements}
    first_session = PrimaryUSSessionCalendar().session_on_or_after(requirements[0].history_start)
    decisions = tuple(
        SignalDecisionTime.for_primary_session(timestamp.date())
        for timestamp in frame.index
        if timestamp.date() >= first_session
    )
    return MarketDataBundle.from_requirements(
        requirements,
        frames,
        decision_time=decisions[-1],
        decision_times=decisions,
    )


@pytest.mark.parametrize("experiment_name", AUXILIARY_FOLLOWUP_EXPERIMENTS)
def test_auxiliary_followup_declares_historical_asof_bundle(
    experiment_name: str,
    historical_bars: pd.DataFrame,
    monkeypatch,
) -> None:
    strategy = get_experiment(experiment_name)
    assert isinstance(strategy, AuxiliaryBundleStrategyMixin)
    requirements = strategy.market_data_requirements()
    assert requirements[0].role == "primary"
    assert len(requirements) > 1
    assert all(item.role == "auxiliary" for item in requirements[1:])
    assert all(
        item.coverage_policy == MarketDataCoveragePolicy.provider_observations()
        for item in requirements[1:]
    )
    assert all(item.availability_policy.publication_lag_sessions == 1 for item in requirements[1:])

    bundle = _bundle(strategy, historical_bars)
    monkeypatch.setattr(
        "trading.market_data.provider.YahooFinanceProvider.fetch",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("auxiliary bundle execution must not contact a provider")
        ),
    )
    result = strategy.run_with_bundle(bundle)
    first_session = PrimaryUSSessionCalendar().session_on_or_after(requirements[0].history_start)
    expected_primary = historical_bars.loc[pd.Timestamp(first_session) :]

    assert result["canonical_sleeve_input"].close_prices.equals(expected_primary["Close"])
    assert result["metadata"]["experiment"] == experiment_name
    for requirement in requirements[1:]:
        aligned = bundle[requirement.series]
        assert len(aligned) == len(expected_primary)
        assert aligned.index.equals(
            pd.DatetimeIndex(expected_primary.index, name="DecisionSession")
        )
        assert aligned.index.name == "DecisionSession"
        assert aligned["ObservationLagSessions"].min() >= 1


@pytest.mark.parametrize("experiment_name", AUXILIARY_FOLLOWUP_EXPERIMENTS)
def test_auxiliary_followup_completes_formal_offline_execution(
    experiment_name: str,
    historical_bars: pd.DataFrame,
    tmp_path,
) -> None:
    strategy = get_experiment(experiment_name)
    requirements = strategy.market_data_requirements()
    refreshed_at = pd.Timestamp("2020-01-07", tz="UTC").to_pydatetime()
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    for requirement in requirements:
        cache.publish(
            requirement.series,
            historical_bars,
            refresh_kind=RefreshKind.FULL,
            refreshed_at=refreshed_at,
            coverage_policy=requirement.coverage_policy,
        )
    definition_store = ResearchDefinitionStore(tmp_path / "blobs")
    definition = strategy.capture_research_definition(definition_store)
    store = ResearchDataStore(tmp_path / "blobs", now=lambda: refreshed_at)
    manifest = store.create_snapshot(
        cache,
        requirements,
        SignalDecisionTime.for_primary_session(historical_bars.index[-1].date()),
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

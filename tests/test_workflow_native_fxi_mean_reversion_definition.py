from dataclasses import asdict
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from trading.policies import PolicyResolver, PolicySet
from trading.research_data import ResearchDefinitionStore
from trading.research_definitions.execution import resolve_workflow_policy_set
from trading.research_definitions.fxi_mean_reversion import (
    FXIMeanReversionTrialConfig,
    build_fxi_mean_reversion_candidate,
    build_fxi_mean_reversion_candidates,
)
from trading.research_definitions.registry import ResearchDefinitionRegistry

V005_WORKFLOW = Path("workflows/strategy-forward-replication-research--v005")


def _config(
    *,
    compound: bool = True,
    holding_sessions: int = 5,
    entry_lag_sessions: int = 1,
    relative_return_floor: float = -0.08,
) -> FXIMeanReversionTrialConfig:
    return FXIMeanReversionTrialConfig(
        ticker="FXI",
        history_start=date(2022, 1, 1),
        research_start=date(2023, 1, 2),
        holding_sessions=holding_sessions,
        entry_lag_sessions=entry_lag_sessions,
        pullback_lookback=10,
        pullback_threshold=-0.05,
        pullback_cap=-0.12,
        wr_period=10,
        wr_threshold=-80.0,
        cooldown_sessions=10,
        profit_target=0.055,
        stop_loss=-0.05,
        close_position_threshold=0.4 if compound else None,
        atr_short_period=5 if compound else None,
        atr_long_period=20 if compound else None,
        atr_ratio_floor=1.05 if compound else None,
        atr_ratio_ceiling=1.35 if compound else None,
        anchor_ticker="ASHR" if compound else None,
        relative_return_lookback=20 if compound else None,
        relative_return_floor=relative_return_floor if compound else None,
    )


def _primary() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", periods=80)
    frame = pd.DataFrame(
        {
            "Open": [100.0] * len(index),
            "High": [101.0] * len(index),
            "Low": [99.0] * len(index),
            "Close": [100.0] * len(index),
            "Volume": [1_000.0] * len(index),
        },
        index=index,
    )
    frame.iloc[30, frame.columns.get_loc("Open")] = 94.0
    frame.iloc[30, frame.columns.get_loc("High")] = 95.0
    frame.iloc[30, frame.columns.get_loc("Low")] = 93.0
    frame.iloc[30, frame.columns.get_loc("Close")] = 94.0
    frame.iloc[31, frame.columns.get_loc("Open")] = 94.0
    frame.iloc[31, frame.columns.get_loc("High")] = 100.0
    frame.iloc[31, frame.columns.get_loc("Low")] = 94.0
    frame.iloc[31, frame.columns.get_loc("Close")] = 99.0
    return frame


def _auxiliary(primary: pd.DataFrame, *, close: float = 100.0, lag: int = 0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": [close] * len(primary),
            "ObservationDate": primary.index,
            "ObservationLagSessions": [lag] * len(primary),
        },
        index=primary.index,
    )


def _policy_set() -> PolicySet:
    resolver = PolicyResolver()
    return PolicySet(
        (
            resolver.resolve("us-equity-market", "v002"),
            resolver.resolve("canonical-execution", "v001"),
            resolver.resolve("firstrade-manual-trading", "v001"),
            resolver.resolve("portfolio-risk", "v001"),
        )
    )


def test_compound_candidate_uses_same_session_ashr_and_next_open_execution() -> None:
    primary = _primary()

    candidates, signals = build_fxi_mean_reversion_candidates(
        primary,
        _auxiliary(primary),
        _config(),
    )

    assert signals == (primary.index[30].date(),)
    candidate = candidates[0]
    assert candidate.entry_date == primary.index[31].date()
    assert candidate.exit_date == primary.index[31].date()
    assert candidate.exit_type == "target"
    assert candidate.exit_price == pytest.approx(94.0 * 1.055)


def test_deeper_ashr_divergence_blocks_the_same_primary_signal() -> None:
    primary = _primary()
    passing, _ = build_fxi_mean_reversion_candidates(
        primary,
        _auxiliary(primary, close=100.0),
        _config(),
    )
    anchor = _auxiliary(primary, close=100.0)
    anchor.iloc[:11, anchor.columns.get_loc("Close")] = 96.0
    blocked, signals = build_fxi_mean_reversion_candidates(primary, anchor, _config())

    assert passing
    assert blocked == ()
    assert signals == ()


def test_pullback_wr_baseline_requires_no_auxiliary_or_compound_gate() -> None:
    candidates, signals = build_fxi_mean_reversion_candidates(
        _primary(), None, _config(compound=False)
    )

    assert signals
    assert len(candidates) == len(signals)


def test_ashr_gate_rejects_nonzero_lag_or_missing_availability_evidence() -> None:
    primary = _primary()

    with pytest.raises(ValueError, match="same completed session"):
        build_fxi_mean_reversion_candidates(primary, _auxiliary(primary, lag=1), _config())
    with pytest.raises(ValueError, match="availability evidence"):
        build_fxi_mean_reversion_candidates(primary, primary, _config())


def test_same_entry_bar_stop_and_target_uses_adverse_stop_first() -> None:
    index = pd.bdate_range("2023-01-02", periods=8)
    primary = pd.DataFrame(
        {
            "Open": [100.0] * len(index),
            "High": [101.0, 106.0, 101.0, 101.0, 101.0, 101.0, 101.0, 101.0],
            "Low": [99.0, 94.0, 99.0, 99.0, 99.0, 99.0, 99.0, 99.0],
            "Close": [100.0] * len(index),
        },
        index=index,
    )

    candidate = build_fxi_mean_reversion_candidate(
        primary, 0, _config(compound=False, holding_sessions=2)
    )

    assert candidate.entry_date == index[1].date()
    assert candidate.exit_date == index[1].date()
    assert candidate.exit_price == 95.0
    assert candidate.exit_type == "stop_loss_pessimistic"


def test_time_expiry_is_the_open_after_post_entry_holding_sessions() -> None:
    index = pd.bdate_range("2023-01-02", periods=8)
    primary = pd.DataFrame(
        {
            "Open": [100.0] * len(index),
            "High": [101.0] * len(index),
            "Low": [99.0] * len(index),
            "Close": [100.0] * len(index),
        },
        index=index,
    )

    candidate = build_fxi_mean_reversion_candidate(
        primary, 0, _config(compound=False, holding_sessions=2)
    )

    assert candidate.entry_date == index[1].date()
    assert candidate.exit_date == index[4].date()
    assert candidate.exit_type == "time_expiry"


def test_entry_lag_can_delay_execution_one_additional_session() -> None:
    index = pd.bdate_range("2023-01-02", periods=9)
    primary = pd.DataFrame(
        {
            "Open": [100.0] * len(index),
            "High": [101.0] * len(index),
            "Low": [99.0] * len(index),
            "Close": [100.0] * len(index),
        },
        index=index,
    )

    candidate = build_fxi_mean_reversion_candidate(
        primary,
        0,
        _config(compound=False, holding_sessions=2, entry_lag_sessions=2),
    )

    assert candidate.entry_date == index[2].date()
    assert candidate.exit_date == index[5].date()
    assert candidate.exit_type == "time_expiry"


def test_config_supports_floor_only_atr_and_rejects_partial_declarations() -> None:
    values = _config(compound=False)

    with pytest.raises(ValueError, match="ATR floor fields"):
        FXIMeanReversionTrialConfig(**{**asdict(values), "atr_short_period": 5})
    floor_only = FXIMeanReversionTrialConfig(
        **{
            **asdict(_config()),
            "atr_ratio_ceiling": None,
            "anchor_ticker": None,
            "relative_return_lookback": None,
            "relative_return_floor": None,
        }
    )
    assert floor_only.atr_ratio_floor == 1.05
    assert floor_only.atr_ratio_ceiling is None
    with pytest.raises(ValueError, match="relative-return fields"):
        FXIMeanReversionTrialConfig(**{**asdict(values), "anchor_ticker": "ASHR"})


def test_registry_loads_six_fixed_identities_and_captures_v004_policy_set(tmp_path: Path) -> None:
    registry = ResearchDefinitionRegistry()
    family = "fxi-atr-divergence-mean-reversion"
    trials = (
        "ashr-floor-minus-7-robustness",
        "ashr-floor-minus-9-robustness",
        "atr-band-ashr-divergence",
        "atr-ceiling-1p30-robustness",
        "hold-18-robustness",
        "pullback-wr-baseline",
    )
    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert [definition.identity for definition in definitions] == [
        f"{family}/{trial}" for trial in trials
    ]
    assert all(definition.family == family for definition in definitions)
    assert all(definition.config.history_start == date(2013, 11, 6) for definition in definitions)
    candidate = registry.load(f"{family}/atr-band-ashr-divergence")
    baseline = registry.load(f"{family}/pullback-wr-baseline")
    assert len(candidate.market_data_requirements()) == 2
    assert candidate.market_data_requirements()[1].availability_policy.publication_lag_sessions == 0
    assert len(baseline.market_data_requirements()) == 1

    snapshot = candidate.capture_research_definition(
        ResearchDefinitionStore(tmp_path / "research-data"),
        _policy_set(),
    )
    assert snapshot.policy_set_identity == _policy_set().identity


def test_registry_loads_and_captures_six_primary_only_atr_band_identities(
    tmp_path: Path,
) -> None:
    registry = ResearchDefinitionRegistry()
    family = "fxi-atr-band-mean-reversion"
    trials = (
        "atr-band-candidate",
        "atr-ceiling-1p30-robustness",
        "atr-floor-1p10-robustness",
        "delay-one-session-robustness",
        "hold-18-robustness",
        "pullback-wr-baseline",
    )
    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert [definition.identity for definition in definitions] == [
        f"{family}/{trial}" for trial in trials
    ]
    assert all(definition.family == family for definition in definitions)
    assert all(len(definition.market_data_requirements()) == 1 for definition in definitions)
    assert all(definition.config.anchor_ticker is None for definition in definitions)
    store = ResearchDefinitionStore(tmp_path / "research-data")
    snapshots = [
        definition.capture_research_definition(store, _policy_set()) for definition in definitions
    ]
    assert all(snapshot.policy_set_identity == _policy_set().identity for snapshot in snapshots)

    candidate = registry.load(f"{family}/atr-band-candidate")
    baseline = registry.load(f"{family}/pullback-wr-baseline")
    delayed = registry.load(f"{family}/delay-one-session-robustness")
    assert candidate.config.atr_ratio_floor == 1.05
    assert candidate.config.atr_ratio_ceiling == 1.35
    assert baseline.config.atr_ratio_floor is None
    assert delayed.config.entry_lag_sessions == 2


def test_registry_loads_six_primary_only_atr_floor_identities(tmp_path: Path) -> None:
    registry = ResearchDefinitionRegistry()
    family = "fxi-atr-floor-mean-reversion"
    trials = (
        "atr-floor-1p10-robustness",
        "atr-floor-candidate",
        "delay-one-session-robustness",
        "hold-18-robustness",
        "pullback-wr-baseline",
        "s001-atr-band-reference",
    )
    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert [definition.identity for definition in definitions] == [
        f"{family}/{trial}" for trial in trials
    ]
    assert all(definition.family == family for definition in definitions)
    assert all(len(definition.market_data_requirements()) == 1 for definition in definitions)
    store = ResearchDefinitionStore(tmp_path / "research-data")
    snapshots = [
        definition.capture_research_definition(store, _policy_set()) for definition in definitions
    ]
    assert all(snapshot.policy_set_identity == _policy_set().identity for snapshot in snapshots)

    candidate = registry.load(f"{family}/atr-floor-candidate")
    stricter = registry.load(f"{family}/atr-floor-1p10-robustness")
    reference = registry.load(f"{family}/s001-atr-band-reference")
    baseline = registry.load(f"{family}/pullback-wr-baseline")
    assert candidate.config.atr_ratio_floor == 1.05
    assert candidate.config.atr_ratio_ceiling is None
    assert stricter.config.atr_ratio_floor == 1.10
    assert stricter.config.atr_ratio_ceiling is None
    assert reference.config.atr_ratio_ceiling == 1.35
    assert baseline.config.atr_ratio_floor is None


def test_registry_loads_six_no_closepos_atr_floor_successor_identities(
    tmp_path: Path,
) -> None:
    registry = ResearchDefinitionRegistry()
    family = "fxi-no-closepos-atr-floor-mean-reversion"
    trials = (
        "no-closepos-atr-floor-1p10-robustness",
        "no-closepos-atr-floor-candidate",
        "no-closepos-cooldown-7-robustness",
        "no-closepos-delay-one-session-robustness",
        "pullback-wr-baseline",
        "s002-closepos-reference",
    )
    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert [definition.identity for definition in definitions] == [
        f"{family}/{trial}" for trial in trials
    ]
    assert all(definition.family == family for definition in definitions)
    assert all(len(definition.market_data_requirements()) == 1 for definition in definitions)
    store = ResearchDefinitionStore(tmp_path / "research-data")
    snapshots = [
        definition.capture_research_definition(store, _policy_set()) for definition in definitions
    ]
    assert all(snapshot.policy_set_identity == _policy_set().identity for snapshot in snapshots)

    candidate = registry.load(f"{family}/no-closepos-atr-floor-candidate")
    stricter = registry.load(f"{family}/no-closepos-atr-floor-1p10-robustness")
    shorter_cooldown = registry.load(f"{family}/no-closepos-cooldown-7-robustness")
    delayed = registry.load(f"{family}/no-closepos-delay-one-session-robustness")
    reference = registry.load(f"{family}/s002-closepos-reference")
    predecessor = registry.load("fxi-atr-floor-mean-reversion/atr-floor-candidate")
    baseline = registry.load(f"{family}/pullback-wr-baseline")

    assert candidate.config.close_position_threshold is None
    assert candidate.config.atr_ratio_floor == 1.05
    assert candidate.config.atr_ratio_ceiling is None
    assert stricter.config.close_position_threshold is None
    assert stricter.config.atr_ratio_floor == 1.10
    assert shorter_cooldown.config.close_position_threshold is None
    assert shorter_cooldown.config.cooldown_sessions == 7
    assert delayed.config.close_position_threshold is None
    assert delayed.config.entry_lag_sessions == 2
    assert asdict(reference.config) == asdict(predecessor.config)
    assert baseline.config.close_position_threshold is None
    assert baseline.config.atr_ratio_floor is None


def test_no_closepos_successor_accepts_signal_excluded_by_s002_reference() -> None:
    registry = ResearchDefinitionRegistry()
    family = "fxi-no-closepos-atr-floor-mean-reversion"
    primary = _primary()
    primary.iloc[30, primary.columns.get_loc("Close")] = 93.2

    candidate = registry.load(f"{family}/no-closepos-atr-floor-candidate")
    reference = registry.load(f"{family}/s002-closepos-reference")
    candidate_trades, candidate_signals = build_fxi_mean_reversion_candidates(
        primary, None, candidate.config
    )
    reference_trades, reference_signals = build_fxi_mean_reversion_candidates(
        primary, None, reference.config
    )

    assert candidate_signals == (primary.index[30].date(),)
    assert len(candidate_trades) == 1
    assert reference_signals == ()
    assert reference_trades == ()


def test_retrospective_family_matches_atr_band_semantics_with_earlier_boundaries(
    tmp_path: Path,
) -> None:
    registry = ResearchDefinitionRegistry()
    source_family = "fxi-atr-band-mean-reversion"
    retrospective_family = "fxi-atr-band-mean-reversion-retrospective"
    trials = (
        "atr-band-candidate",
        "atr-ceiling-1p30-robustness",
        "atr-floor-1p10-robustness",
        "delay-one-session-robustness",
        "hold-18-robustness",
        "pullback-wr-baseline",
    )

    store = ResearchDefinitionStore(tmp_path / "research-data")
    for trial in trials:
        source = registry.load(f"{source_family}/{trial}")
        retrospective = registry.load(f"{retrospective_family}/{trial}")
        source_config = asdict(source.config)
        retrospective_config = asdict(retrospective.config)

        assert retrospective.identity == f"{retrospective_family}/{trial}"
        assert retrospective.family == retrospective_family
        assert retrospective.config.history_start == date(2009, 1, 2)
        assert retrospective.config.research_start == date(2010, 1, 4)
        source_config.pop("history_start")
        source_config.pop("research_start")
        retrospective_config.pop("history_start")
        retrospective_config.pop("research_start")
        assert retrospective_config == source_config
        assert len(retrospective.market_data_requirements()) == 1
        assert retrospective.config.anchor_ticker is None

        source_candidates, source_signals = build_fxi_mean_reversion_candidates(
            _primary(), None, source.config
        )
        retrospective_candidates, retrospective_signals = build_fxi_mean_reversion_candidates(
            _primary(), None, retrospective.config
        )
        assert retrospective_signals == source_signals
        assert retrospective_candidates == source_candidates

        policy_set = resolve_workflow_policy_set(V005_WORKFLOW)
        snapshot = retrospective.capture_research_definition(store, policy_set)
        assert snapshot.policy_set_identity == policy_set.identity
        assert policy_set.identity == _policy_set().identity


def test_retrospective_family_is_complete_and_does_not_mutate_source_family() -> None:
    registry = ResearchDefinitionRegistry()
    retrospective = tuple(
        identity
        for identity in registry.list_trials()
        if identity.startswith("fxi-atr-band-mean-reversion-retrospective/")
    )

    assert retrospective == (
        "fxi-atr-band-mean-reversion-retrospective/atr-band-candidate",
        "fxi-atr-band-mean-reversion-retrospective/atr-ceiling-1p30-robustness",
        "fxi-atr-band-mean-reversion-retrospective/atr-floor-1p10-robustness",
        "fxi-atr-band-mean-reversion-retrospective/delay-one-session-robustness",
        "fxi-atr-band-mean-reversion-retrospective/hold-18-robustness",
        "fxi-atr-band-mean-reversion-retrospective/pullback-wr-baseline",
    )
    assert registry.load(
        "fxi-atr-band-mean-reversion/atr-band-candidate"
    ).config.research_start == date(2015, 1, 2)

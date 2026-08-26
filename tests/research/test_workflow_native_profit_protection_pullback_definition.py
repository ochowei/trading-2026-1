from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from trading.core.sleeve_engine import CanonicalSleeveEngine
from trading.policies import PolicyResolver, PolicySet
from trading.research_data import ResearchDefinitionStore
from trading.research_definitions.profit_protection_pullback import (
    ProfitProtectionPullbackResearchDefinition,
    ProfitProtectionPullbackTrialConfig,
    build_profit_protection_candidate,
    build_profit_protection_candidates,
)
from trading.research_definitions.registry import ResearchDefinitionRegistry


def _config(
    *,
    arm_return: float | None = 0.02,
    floor_return: float | None = 0.005,
    protection_exit_lag_sessions: int = 1,
    holding_sessions: int = 5,
) -> ProfitProtectionPullbackTrialConfig:
    return ProfitProtectionPullbackTrialConfig(
        ticker="XLF",
        history_start=date(2022, 1, 1),
        research_start=date(2023, 1, 2),
        holding_sessions=holding_sessions,
        entry_lag_sessions=1,
        pullback_lookback=10,
        pullback_threshold=-0.04,
        bollinger_lookback=20,
        bollinger_stddevs=2.0,
        arm_return=arm_return,
        floor_return=floor_return,
        protection_exit_lag_sessions=protection_exit_lag_sessions,
    )


def _frame(opens: list[float], closes: list[float]) -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", periods=len(opens))
    return pd.DataFrame({"Open": opens, "Close": closes}, index=index)


def _signal_frame() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", periods=60)
    closes = [100.0] * 25 + [99.0, 98.0, 97.0, 96.0, 95.0] + [94.0] * 30
    return pd.DataFrame({"Open": closes, "Close": closes}, index=index)


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


def test_profit_protection_arms_then_exits_at_the_next_open_after_a_later_floor_close() -> None:
    primary = _frame(
        [100.0, 100.0, 101.5, 100.8, 99.5, 99.0, 98.0],
        [100.0, 102.1, 101.0, 100.4, 99.5, 99.0, 98.0],
    )

    candidate = build_profit_protection_candidate(primary, 0, _config())

    assert candidate.entry_date == primary.index[1].date()
    assert candidate.exit_date == primary.index[4].date()
    assert candidate.exit_price == 99.5
    assert candidate.exit_type == "profit_protection"


def test_floor_close_on_the_arming_session_cannot_fire_protection() -> None:
    primary = _frame(
        [100.0, 100.0, 101.0, 100.0, 99.0, 98.0, 97.0],
        [100.0, 102.1, 102.2, 100.4, 99.0, 98.0, 97.0],
    )

    candidate = build_profit_protection_candidate(primary, 0, _config())

    assert candidate.exit_date == primary.index[4].date()
    assert candidate.exit_type == "profit_protection"


def test_fixed_baseline_uses_only_the_ten_session_expiry() -> None:
    primary = _frame(
        [100.0, 100.0, 101.5, 100.8, 99.5, 99.0, 98.0],
        [100.0, 102.1, 101.0, 100.4, 99.5, 99.0, 98.0],
    )
    config = _config(arm_return=None, floor_return=None)

    candidate = build_profit_protection_candidate(primary, 0, config)

    assert candidate.exit_date == primary.index[6].date()
    assert candidate.exit_type == "time_expiry"


def test_delayed_robustness_waits_one_additional_session_before_exit() -> None:
    primary = _frame(
        [100.0, 100.0, 101.5, 100.8, 99.5, 98.5, 98.0],
        [100.0, 102.1, 101.0, 100.4, 99.5, 98.5, 98.0],
    )

    candidate = build_profit_protection_candidate(
        primary,
        0,
        _config(protection_exit_lag_sessions=2),
    )

    assert candidate.exit_date == primary.index[5].date()
    assert candidate.exit_type == "profit_protection"


def test_protection_scheduled_for_expiry_remains_a_time_expiry() -> None:
    primary = _frame(
        [100.0, 100.0, 101.5, 101.0, 100.8, 100.6, 99.0],
        [100.0, 102.1, 101.5, 101.0, 100.8, 100.4, 99.0],
    )

    candidate = build_profit_protection_candidate(primary, 0, _config())

    assert candidate.exit_date == primary.index[6].date()
    assert candidate.exit_type == "time_expiry"


def test_occupation_lock_keeps_candidate_and_baseline_entry_cohorts_identical() -> None:
    primary = _signal_frame()
    initial = build_profit_protection_candidates(
        primary,
        _config(arm_return=None, floor_return=None),
    )
    first_entry = initial.candidates[0].entry_date
    primary.loc[pd.Timestamp(first_entry), "Open"] = 90.0

    protected = build_profit_protection_candidates(
        primary,
        _config(arm_return=0.05, floor_return=0.049),
    )
    baseline = build_profit_protection_candidates(
        primary,
        _config(arm_return=None, floor_return=None),
    )

    assert protected.raw_signals == baseline.raw_signals
    assert protected.occupation_lock_skips == baseline.occupation_lock_skips
    assert [item.entry_date for item in protected.candidates] == [
        item.entry_date for item in baseline.candidates
    ]
    assert protected.occupation_lock_skips
    assert protected.candidates[0].exit_type == "profit_protection"

    protected_execution = CanonicalSleeveEngine().run(
        calendar=primary.index,
        close_prices=primary["Close"],
        candidates=protected.candidates,
    )
    baseline_execution = CanonicalSleeveEngine().run(
        calendar=primary.index,
        close_prices=primary["Close"],
        candidates=baseline.candidates,
    )
    assert [
        trade.entry_date for trade in protected_execution.trades if trade.status != "skipped"
    ] == [trade.entry_date for trade in baseline_execution.trades if trade.status != "skipped"]


def test_definition_records_occupation_lock_diagnostics_without_auxiliary_data() -> None:
    definition = ProfitProtectionPullbackResearchDefinition(
        identity="test/profit-protection",
        result_name="test-profit-protection",
        family="test-profit-protection",
        hypothesis="test",
        config=_config(),
        source_path=Path(__file__),
    )
    primary = _signal_frame()

    class Bundle:
        def __iter__(self):
            return iter((definition.market_data_requirements()[0].series,))

        def __getitem__(self, series):
            return primary

    result = definition.run_with_bundle(Bundle())
    sleeve = result["canonical_sleeve_input"]

    assert len(definition.market_data_requirements()) == 1
    assert result["metadata"]["auxiliary_ticker"] is None
    assert result["metadata"]["occupation_lock_skips"]
    assert (
        tuple(item.isoformat() for item in sleeve.raw_signals)
        != result["metadata"]["accepted_entry_dates"]
    )


def test_nonfinite_entry_or_exit_open_fails_closed() -> None:
    primary = _frame(
        [100.0, float("nan"), 101.5, 100.8, 99.5, 99.0, 98.0],
        [100.0, 102.1, 101.0, 100.4, 99.5, 99.0, 98.0],
    )

    with pytest.raises(ValueError, match="entry open"):
        build_profit_protection_candidate(primary, 0, _config())

    primary.loc[primary.index[1], "Open"] = 100.0
    primary.loc[primary.index[4], "Open"] = float("nan")
    with pytest.raises(ValueError, match="exit open"):
        build_profit_protection_candidate(primary, 0, _config())


def test_config_rejects_partial_or_invalid_protection_state() -> None:
    with pytest.raises(ValueError, match="floor_return"):
        _config(floor_return=None)
    with pytest.raises(ValueError, match="below arm_return"):
        _config(arm_return=0.02, floor_return=0.02)
    with pytest.raises(ValueError, match="fixed baseline"):
        _config(
            arm_return=None,
            floor_return=None,
            protection_exit_lag_sessions=2,
        )


def test_family_exposes_exact_five_policy_bound_source_identities(tmp_path: Path) -> None:
    family = "xlf-close-armed-profit-protection-pullback"
    trials = (
        "arm-1p5-floor-0p5-robustness",
        "arm-2p5-floor-0p5-robustness",
        "close-armed-2-floor-0p5",
        "delayed-protection-exit-robustness",
        "fixed-ten-session-baseline",
    )
    registry = ResearchDefinitionRegistry()

    definitions = [registry.load(f"{family}/{trial}") for trial in trials]
    snapshots = [
        definition.capture_research_definition(
            ResearchDefinitionStore(tmp_path / trial),
            _policy_set(),
        )
        for trial, definition in zip(trials, definitions, strict=True)
    ]

    assert [definition.identity for definition in definitions] == [
        f"{family}/{trial}" for trial in trials
    ]
    assert all(definition.family == family for definition in definitions)
    assert all(definition.config.history_start == date(2002, 11, 13) for definition in definitions)
    assert all(definition.config.research_start == date(2004, 1, 2) for definition in definitions)
    assert all(len(definition.market_data_requirements()) == 1 for definition in definitions)
    assert all(snapshot.policy_set_identity == _policy_set().identity for snapshot in snapshots)

    configs = {
        definition.identity.rsplit("/", 1)[-1]: definition.config for definition in definitions
    }
    assert configs["close-armed-2-floor-0p5"].arm_return == 0.02
    assert configs["fixed-ten-session-baseline"].arm_return is None
    assert configs["arm-1p5-floor-0p5-robustness"].arm_return == 0.015
    assert configs["arm-2p5-floor-0p5-robustness"].arm_return == 0.025
    assert configs["delayed-protection-exit-robustness"].protection_exit_lag_sessions == 2

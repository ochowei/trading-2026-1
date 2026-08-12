from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from trading.policies import PolicyResolver, PolicySet
from trading.research_data import ResearchDefinitionStore
from trading.research_definitions.rate_volatility_pullback import (
    RateVolatilityPullbackTrialConfig,
    build_rate_volatility_candidates,
)
from trading.research_definitions.rate_volatility_pullback_gap_safe import (
    GapSafeRateVolatilityPullbackResearchDefinition,
)
from trading.research_definitions.registry import ResearchDefinitionRegistry


def _primary() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", periods=45)
    closes = [100.0] * 25 + [99.0, 98.0, 97.0, 96.0, 95.0] + [94.0] * 15
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [value + 1 for value in closes],
            "Low": [value - 1 for value in closes],
            "Close": closes,
            "Volume": [100.0] * len(index),
        },
        index=index,
    )


def _auxiliary(primary: pd.DataFrame, jump: float) -> pd.DataFrame:
    values = [100.0 + max(position - 24, 0) * jump / 3 for position in range(len(primary))]
    return pd.DataFrame(
        {
            "Close": values,
            "ObservationDate": primary.index - pd.offsets.BDay(1),
            "ObservationLagSessions": [1] * len(primary),
        },
        index=primary.index,
    )


def _config(cap: float | None, *, entry_lag_sessions: int = 1):
    return RateVolatilityPullbackTrialConfig(
        ticker="XLF",
        history_start=date(2022, 1, 1),
        research_start=date(2023, 1, 1),
        holding_sessions=5,
        entry_lag_sessions=entry_lag_sessions,
        pullback_lookback=10,
        pullback_threshold=-0.04,
        bollinger_lookback=20,
        bollinger_stddevs=2.0,
        move_ticker="^MOVE" if cap is not None else None,
        move_change_sessions=3 if cap is not None else None,
        move_change_cap=cap,
    )


def test_move_gate_uses_backward_as_of_observations_and_next_open_execution() -> None:
    primary = _primary()
    candidates, signals = build_rate_volatility_candidates(
        primary,
        _auxiliary(primary, 5.0),
        _config(5.0),
    )

    assert signals
    first = candidates[0]
    signal_position = primary.index.get_loc(pd.Timestamp(first.signal_date))
    assert first.entry_date == primary.index[signal_position + 1].date()
    assert first.exit_date == primary.index[signal_position + 6].date()
    assert first.exit_type == "time_expiry"


def test_tighter_move_cap_can_block_the_same_synthetic_pullback() -> None:
    primary = _primary()

    loose, _ = build_rate_volatility_candidates(primary, _auxiliary(primary, 5.0), _config(5.0))
    tight, _ = build_rate_volatility_candidates(primary, _auxiliary(primary, 5.0), _config(3.0))

    assert loose
    assert len(tight) < len(loose)


def test_ungated_baseline_does_not_require_auxiliary_data() -> None:
    candidates, signals = build_rate_volatility_candidates(_primary(), None, _config(None))

    assert candidates
    assert len(candidates) == len(signals)


def test_gated_definition_rejects_unaligned_or_unproven_auxiliary_data() -> None:
    primary = _primary()

    with pytest.raises(ValueError, match="availability evidence"):
        build_rate_volatility_candidates(primary, primary, _config(5.0))


def test_config_rejects_partial_move_gate_declarations() -> None:
    with pytest.raises(ValueError, match="declared together"):
        RateVolatilityPullbackTrialConfig(
            ticker="XLF",
            history_start=date(2022, 1, 1),
            research_start=date(2023, 1, 1),
            holding_sessions=10,
            entry_lag_sessions=1,
            pullback_lookback=10,
            pullback_threshold=-0.04,
            bollinger_lookback=20,
            bollinger_stddevs=2.0,
            move_ticker="^MOVE",
        )


def test_revised_availability_family_has_new_stable_identities_and_correct_history_start() -> None:
    registry = ResearchDefinitionRegistry()
    family = "xlf-rate-volatility-conditioned-pullback-revised-availability"
    trials = (
        "move-direction-cap-3",
        "move-direction-cap-5",
        "move-direction-cap-7",
        "ungated-pullback-baseline",
    )

    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert all(definition.family == family for definition in definitions)
    assert all(
        requirement.history_start == date(1998, 12, 22)
        for definition in definitions
        for requirement in definition.market_data_requirements()
    )
    assert registry.load(
        "xlf-rate-volatility-conditioned-pullback/move-direction-cap-3"
    ).config.history_start == date(1998, 12, 16)


def test_publication_lag_safe_family_starts_after_first_move_observation() -> None:
    registry = ResearchDefinitionRegistry()
    family = "xlf-rate-volatility-conditioned-pullback-publication-lag-safe"
    trials = (
        "move-direction-cap-3",
        "move-direction-cap-5",
        "move-direction-cap-7",
        "ungated-pullback-baseline",
    )

    definitions = [registry.load(f"{family}/{trial}") for trial in trials]

    assert all(definition.family == family for definition in definitions)
    assert all(definition.config.history_start == date(2002, 11, 13) for definition in definitions)
    assert all(definition.config.research_start == date(2004, 1, 2) for definition in definitions)
    assert registry.load(
        "xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-3"
    ).config.history_start == date(1998, 12, 22)


def test_gap_safe_definition_removes_only_over_age_signal_decisions() -> None:
    primary = _primary()
    auxiliary = _auxiliary(primary, 5.0)
    candidates, signals = build_rate_volatility_candidates(primary, auxiliary, _config(5.0))
    assert candidates
    blocked_signal = signals[0]
    auxiliary["ObservationAvailable"] = True
    auxiliary.loc[pd.Timestamp(blocked_signal), "ObservationAvailable"] = False
    definition = GapSafeRateVolatilityPullbackResearchDefinition(
        identity="test/gap-safe",
        result_name="test-gap-safe",
        family="test-gap-safe",
        hypothesis="test",
        config=_config(5.0),
        source_path=Path(__file__),
    )

    class Bundle:
        def __iter__(self):
            return iter(requirement.series for requirement in definition.market_data_requirements())

        def __getitem__(self, series):
            return primary if series.symbol == "XLF" else auxiliary

    sleeve = definition.run_with_bundle(Bundle())["canonical_sleeve_input"]

    assert blocked_signal not in sleeve.raw_signals
    assert all(candidate.signal_date != blocked_signal for candidate in sleeve.candidates)
    assert len(sleeve.raw_signals) == len(signals) - 1


def test_gap_safe_definition_rejects_v001_market_policy(tmp_path) -> None:
    definition = GapSafeRateVolatilityPullbackResearchDefinition(
        identity="test/gap-safe-v001",
        result_name="test-gap-safe-v001",
        family="test-gap-safe-v001",
        hypothesis="test",
        config=_config(5.0),
        source_path=Path(__file__),
    )
    resolver = PolicyResolver()
    policy_set = PolicySet(
        (
            resolver.resolve("us-equity-market", "v001"),
            resolver.resolve("canonical-execution", "v001"),
            resolver.resolve("firstrade-manual-trading", "v001"),
            resolver.resolve("portfolio-risk", "v001"),
        )
    )

    with pytest.raises(ValueError, match="require us-equity-market@v002"):
        definition.capture_research_definition(
            ResearchDefinitionStore(tmp_path / "research-data"), policy_set
        )

from trading.core.sleeve_engine import DEFAULT_BASE_COST_POLICY, DEFAULT_STRESS_COST_POLICY


def test_canonical_execution_v001_pins_base_and_stress_costs() -> None:
    assert (
        DEFAULT_BASE_COST_POLICY.entry_slippage_bps,
        DEFAULT_BASE_COST_POLICY.exit_slippage_bps,
        DEFAULT_BASE_COST_POLICY.fee_bps_per_side,
    ) == (5.0, 5.0, 1.0)
    assert (
        DEFAULT_STRESS_COST_POLICY.entry_slippage_bps,
        DEFAULT_STRESS_COST_POLICY.exit_slippage_bps,
        DEFAULT_STRESS_COST_POLICY.fee_bps_per_side,
    ) == (20.0, 20.0, 2.0)

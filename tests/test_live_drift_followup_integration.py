from datetime import UTC, datetime

from trading.core.followup_cutover import (
    FollowupAuthorizationContext,
    FollowupLifecycleRegistry,
    FollowupStrategy,
    StrategyLifecycle,
    authorize_followup_order,
)
from trading.core.ledger_storage import locked_file
from trading.core.live_drift import (
    DriftDirection,
    DriftMetricExpectation,
    DriftState,
    PredictiveDriftEnvelope,
)
from trading.core.live_drift_registry import LiveDriftRegistry


def _context(**overrides: object) -> FollowupAuthorizationContext:
    values: dict[str, object] = {
        "lifecycle": StrategyLifecycle.ACTIVE,
        "no_new_entry": False,
        "result_valid": True,
        "result_identity": "result:spy:1",
        "active_proof_current": True,
        "data_fresh": True,
        "data_cutoff": "2026-09-08",
        "data_bundle_identity": "bundle:1",
        "ledger_verified": True,
        "ledger_accounting_hash": "ledger:1",
        "broker_reconciled": True,
        "proposal_epoch_current": True,
        "has_actual_position": False,
        "drift_state": DriftState.PAUSED,
        "drift_hard_guards_clear": True,
        "drift_envelope_id": "e" * 64,
        "drift_checkpoint_id": "c" * 64,
    }
    values.update(overrides)
    return FollowupAuthorizationContext(**values)  # type: ignore[arg-type]


def test_paused_drift_suppresses_buy_but_preserves_verified_existing_sell() -> None:
    buy = authorize_followup_order("BUY", _context())
    sell = authorize_followup_order("SELL", _context(has_actual_position=True))

    assert buy.authorized is False
    assert buy.reason == "live drift is paused"
    assert sell.authorized is True
    assert sell.reason == "verified actual-position exit"


def test_watch_drift_remains_buy_eligible_when_every_other_guard_passes() -> None:
    decision = authorize_followup_order("BUY", _context(drift_state=DriftState.WATCH))

    assert decision.authorized is True


def test_buy_revalidation_can_read_lifecycle_and_drift_under_shared_coordination_lock(
    tmp_path,
) -> None:
    lifecycle = FollowupLifecycleRegistry(
        tmp_path / "followup-lifecycle.json",
        lock_timeout_seconds=0.1,
    )
    lifecycle.initialize_cutover(
        (FollowupStrategy("SPY", "spy_007_trend_pullback"),),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    drift = LiveDriftRegistry(
        tmp_path / "live-drift" / "spy.json",
        lock_timeout_seconds=0.1,
    )
    drift.freeze_envelope(
        PredictiveDriftEnvelope.create(
            strategy_id="SPY/spy_007_trend_pullback",
            definition_fingerprint="a" * 64,
            source_identities=("historical-screen:plan-1", "shadow-evidence:shadow-1:1"),
            metrics=(
                DriftMetricExpectation.create(
                    metric_id="performance_return",
                    direction=DriftDirection.LOWER_IS_WORSE,
                    watch_boundary="-0.20",
                    pause_boundary="-0.40",
                    minimum_observations=1,
                    window_sessions=21,
                ),
            ),
            activation_anchor=datetime(2026, 8, 7, tzinfo=UTC).date(),
            checkpoint_interval_sessions=21,
            bootstrap_seed=7,
            bootstrap_repetitions=1000,
            bootstrap_block_sessions=5,
            frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
        )
    )
    assert lifecycle.coordination_lock_path == drift.coordination_lock_path

    with locked_file(lifecycle.coordination_lock_path, 0.1):
        lifecycle_state = lifecycle.read_while_coordinated()
        drift_state = drift.read_while_coordinated()

    assert lifecycle_state.no_new_entry is True
    assert drift_state.state is DriftState.PAUSED

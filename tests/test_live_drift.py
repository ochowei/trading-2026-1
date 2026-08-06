import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from trading.core.live_drift import (
    DriftAssessment,
    DriftDirection,
    DriftMetricExpectation,
    DriftMetricKind,
    DriftMetricObservation,
    DriftObservation,
    DriftState,
    HardGuardKind,
    HardGuardObservation,
    PredictiveDriftEnvelope,
    evaluate_checkpoint,
    evaluate_recovery,
)
from trading.core.live_drift_registry import (
    LiveDriftRegistry,
    LiveDriftRegistryError,
    verify_envelope_qualification_sources,
)
from trading.market_data import PrimaryUSSessionCalendar


def _metric() -> DriftMetricExpectation:
    return DriftMetricExpectation.create(
        metric_id="performance_return",
        direction=DriftDirection.LOWER_IS_WORSE,
        watch_boundary=Decimal("-0.20"),
        pause_boundary=Decimal("-0.40"),
        minimum_observations=6,
        window_sessions=126,
    )


def test_envelope_identity_is_canonical_and_decimal_only() -> None:
    first = PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("shadow-1", "historical-plan-1"),
        metrics=(_metric(),),
        activation_anchor=date(2026, 8, 7),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    second = PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("historical-plan-1", "shadow-1"),
        metrics=(_metric(),),
        activation_anchor=date(2026, 8, 7),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )

    assert first.envelope_id == second.envelope_id
    assert first.payload() == second.payload()
    assert first.metrics[0].watch_boundary == Decimal("-0.20")

    with pytest.raises(TypeError, match="Decimal"):
        DriftMetricExpectation.create(
            metric_id="bad",
            direction=DriftDirection.LOWER_IS_WORSE,
            watch_boundary=-0.2,
            pause_boundary=-0.4,
            minimum_observations=1,
            window_sessions=1,
        )
    with pytest.raises(TypeError, match="Decimal"):
        DriftMetricObservation.create(metric_id="bad", value=0.1, sample_count=1)


def test_activation_envelope_sources_must_match_verified_historical_and_shadow_events() -> None:
    envelope = _envelope()
    qualification_state = {
        "events": [
            {
                "event_id": "historical-screen:plan-1",
                "event_type": "historical_screen",
                "payload": {"plan_id": "plan-1", "passed": True},
            },
            {
                "event_id": "shadow-registration:shadow-1",
                "event_type": "shadow_registration",
                "payload": {
                    "shadow_id": "shadow-1",
                    "historical_plan_id": "plan-1",
                    "definition_fingerprint": envelope.definition_fingerprint,
                },
            },
            {
                "event_id": "shadow-evidence:shadow-1:2026-08-06",
                "event_type": "shadow_evidence",
                "payload": {
                    "shadow_id": "shadow-1",
                    "definition_fingerprint": envelope.definition_fingerprint,
                    "as_of": "2026-08-06",
                    "simulated_fills": [],
                },
            },
            {
                "event_id": "activation-evaluation:shadow-1:2026-08-06",
                "event_type": "activation_evaluation",
                "payload": {
                    "shadow_id": "shadow-1",
                    "evaluated_at": "2026-08-06",
                    "eligible": True,
                    "disposition": "activation-eligible",
                },
            },
        ]
    }

    with pytest.raises(LiveDriftRegistryError, match="source identities"):
        verify_envelope_qualification_sources(
            envelope,
            qualification_state=qualification_state,
            shadow_id="shadow-1",
            activation_event_id="activation-evaluation:shadow-1:2026-08-06",
        )

    source_bound_but_incomplete = PredictiveDriftEnvelope.create(
        strategy_id=envelope.strategy_id,
        definition_fingerprint=envelope.definition_fingerprint,
        source_identities=(
            "historical-screen:plan-1",
            "shadow-evidence:shadow-1:2026-08-06",
        ),
        metrics=envelope.metrics,
        activation_anchor=envelope.activation_anchor,
        checkpoint_interval_sessions=envelope.checkpoint_interval_sessions,
        bootstrap_seed=envelope.bootstrap_seed,
        bootstrap_repetitions=envelope.bootstrap_repetitions,
        bootstrap_block_sessions=envelope.bootstrap_block_sessions,
        frozen_at=datetime(2026, 8, 7, 21, 0, tzinfo=UTC),
    )
    with pytest.raises(LiveDriftRegistryError, match="metric families"):
        verify_envelope_qualification_sources(
            source_bound_but_incomplete,
            qualification_state=qualification_state,
            shadow_id="shadow-1",
            activation_event_id="activation-evaluation:shadow-1:2026-08-06",
        )

    extra_metrics = tuple(
        DriftMetricExpectation.create(
            metric_id=kind.value,
            kind=kind,
            direction=DriftDirection.HIGHER_IS_WORSE,
            watch_boundary="0.20",
            pause_boundary="0.40",
            minimum_observations=1,
            window_sessions=21,
        )
        for kind in (
            DriftMetricKind.SIGNAL,
            DriftMetricKind.EXECUTION,
            DriftMetricKind.UTILIZATION,
            DriftMetricKind.CONCENTRATION,
        )
    )
    bound = PredictiveDriftEnvelope.create(
        strategy_id=envelope.strategy_id,
        definition_fingerprint=envelope.definition_fingerprint,
        source_identities=source_bound_but_incomplete.source_identities,
        metrics=(*envelope.metrics, *extra_metrics),
        activation_anchor=envelope.activation_anchor,
        checkpoint_interval_sessions=envelope.checkpoint_interval_sessions,
        bootstrap_seed=envelope.bootstrap_seed,
        bootstrap_repetitions=envelope.bootstrap_repetitions,
        bootstrap_block_sessions=envelope.bootstrap_block_sessions,
        frozen_at=source_bound_but_incomplete.frozen_at,
    )
    verify_envelope_qualification_sources(
        bound,
        qualification_state=qualification_state,
        shadow_id="shadow-1",
        activation_event_id="activation-evaluation:shadow-1:2026-08-06",
    )


def test_all_drift_metric_families_use_the_same_frozen_decimal_boundaries() -> None:
    metrics = tuple(
        DriftMetricExpectation.create(
            metric_id=metric_id,
            kind=kind,
            direction=direction,
            watch_boundary=watch,
            pause_boundary=pause,
            minimum_observations=1,
            window_sessions=21,
        )
        for metric_id, kind, direction, watch, pause in (
            (
                "performance",
                DriftMetricKind.PERFORMANCE,
                DriftDirection.LOWER_IS_WORSE,
                "-0.20",
                "-0.40",
            ),
            (
                "signal",
                DriftMetricKind.SIGNAL,
                DriftDirection.HIGHER_IS_WORSE,
                "0.20",
                "0.40",
            ),
            (
                "execution",
                DriftMetricKind.EXECUTION,
                DriftDirection.HIGHER_IS_WORSE,
                "0.20",
                "0.40",
            ),
            (
                "utilization",
                DriftMetricKind.UTILIZATION,
                DriftDirection.HIGHER_IS_WORSE,
                "0.80",
                "0.95",
            ),
            (
                "concentration",
                DriftMetricKind.CONCENTRATION,
                DriftDirection.HIGHER_IS_WORSE,
                "0.60",
                "0.80",
            ),
        )
    )
    envelope = PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("folds", "shadow"),
        metrics=metrics,
        activation_anchor=date(2026, 8, 7),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    observations = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 20, 0, tzinfo=UTC),
        metrics=tuple(
            DriftMetricObservation.create(
                metric_id=metric.metric_id,
                value="-0.20" if metric.direction is DriftDirection.LOWER_IS_WORSE else "0.20",
                sample_count=1,
            )
            for metric in metrics
        ),
    )

    checkpoint = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(observations,),
    )

    assert checkpoint.assessment is DriftAssessment.WATCH
    assert {item.metric_id for item in checkpoint.metric_assessments} == {
        "performance",
        "signal",
        "execution",
        "utilization",
        "concentration",
    }


def _envelope() -> PredictiveDriftEnvelope:
    return PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("shadow-1", "historical-plan-1"),
        metrics=(
            DriftMetricExpectation.create(
                metric_id="performance_return",
                kind=DriftMetricKind.PERFORMANCE,
                direction=DriftDirection.LOWER_IS_WORSE,
                watch_boundary=Decimal("-0.20"),
                pause_boundary=Decimal("-0.40"),
                minimum_observations=1,
                window_sessions=126,
            ),
        ),
        activation_anchor=date(2026, 8, 7),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )


def _observation(
    envelope: PredictiveDriftEnvelope,
    *,
    session: date,
    value: str = "0",
    guards: tuple[HardGuardObservation, ...] = (),
) -> DriftObservation:
    return DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=session,
        observed_at=datetime.combine(session, datetime.min.time(), tzinfo=UTC)
        + timedelta(hours=21),
        metrics=(
            DriftMetricObservation.create(
                metric_id="performance_return",
                value=value,
                sample_count=1,
            ),
        ),
        hard_guards=guards,
    )


def test_checkpoint_uses_inclusive_watch_and_pause_boundaries() -> None:
    envelope = _envelope()

    watch = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(_observation(envelope, session=date(2026, 9, 8), value="-0.20"),),
    )
    paused = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(_observation(envelope, session=date(2026, 9, 8), value="-0.40"),),
    )

    assert watch.assessment is DriftAssessment.WATCH
    assert watch.state is DriftState.WATCH
    assert paused.assessment is DriftAssessment.PAUSED
    assert paused.state is DriftState.PAUSED


def test_ordinary_single_loss_inside_envelope_is_not_a_pause() -> None:
    envelope = _envelope()
    checkpoint = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(_observation(envelope, session=date(2026, 9, 8), value="-0.05"),),
    )

    assert checkpoint.assessment is DriftAssessment.NORMAL
    assert checkpoint.state is DriftState.HEALTHY


def test_checkpoint_does_not_reuse_metric_outside_its_frozen_session_window() -> None:
    envelope = PredictiveDriftEnvelope.create(
        strategy_id="SPY/spy_007_trend_pullback",
        definition_fingerprint="a" * 64,
        source_identities=("historical-plan-1", "shadow-1"),
        metrics=(
            DriftMetricExpectation.create(
                metric_id="performance_return",
                direction=DriftDirection.LOWER_IS_WORSE,
                watch_boundary="-0.20",
                pause_boundary="-0.40",
                minimum_observations=1,
                window_sessions=1,
            ),
        ),
        activation_anchor=date(2026, 8, 7),
        checkpoint_interval_sessions=21,
        bootstrap_seed=7,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=5,
        frozen_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    checkpoint_session = envelope.expected_checkpoint(1)
    prior_session = PrimaryUSSessionCalendar().session_offset(checkpoint_session, -1)

    checkpoint = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=checkpoint_session,
        observations=(_observation(envelope, session=prior_session, value="0"),),
    )

    assert checkpoint.assessment is DriftAssessment.INCONCLUSIVE
    assert checkpoint.state is DriftState.WATCH


def test_two_watch_checkpoints_pause_without_manual_state_edit() -> None:
    envelope = _envelope()
    first = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(_observation(envelope, session=date(2026, 9, 8), value="-0.20"),),
    )
    second = evaluate_checkpoint(
        envelope,
        ordinal=2,
        session=date(2026, 10, 7),
        observations=(_observation(envelope, session=date(2026, 10, 7), value="-0.20"),),
        prior_state=first.state,
        prior_watch_streak=first.watch_streak,
    )

    assert first.state is DriftState.WATCH
    assert second.assessment is DriftAssessment.PAUSED
    assert second.state is DriftState.PAUSED


def test_two_consecutive_inconclusive_watch_checkpoints_pause_fail_closed() -> None:
    envelope = _envelope()
    first = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=envelope.expected_checkpoint(1),
        observations=(),
    )
    second = evaluate_checkpoint(
        envelope,
        ordinal=2,
        session=envelope.expected_checkpoint(2),
        observations=(),
        prior_state=first.state,
        prior_watch_streak=first.watch_streak,
    )

    assert first.state is DriftState.WATCH
    assert first.watch_streak == 1
    assert second.state is DriftState.PAUSED
    assert second.watch_streak == 2


def test_hard_guard_pauses_immediately_at_checkpoint() -> None:
    envelope = _envelope()
    guard = HardGuardObservation.create(
        kind=HardGuardKind.RECONCILIATION,
        guard_id="reconciliation-current",
        active=True,
        evidence_identity="broker-export-1",
        reason="broker reconciliation is stale",
    )
    checkpoint = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(_observation(envelope, session=date(2026, 9, 8), guards=(guard,)),),
    )

    assert checkpoint.state is DriftState.PAUSED
    assert checkpoint.active_hard_guards == (guard,)


def test_registry_replays_frozen_envelope_observation_and_checkpoint(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    observation = _observation(
        envelope,
        session=date(2026, 9, 8),
        value="-0.05",
    )
    registry.record_observation(observation)
    registry.record_observation(observation)
    checkpoint = registry.record_checkpoint(ordinal=1, session=date(2026, 9, 8))

    replayed = LiveDriftRegistry(tmp_path / "live-drift.json").read()
    assert replayed.envelope == envelope
    assert replayed.activation_event_id == "activation-1"
    assert replayed.observations == (observation,)
    assert replayed.checkpoints == (checkpoint,)
    assert replayed.state is DriftState.HEALTHY
    assert replayed.buy_allowed is True


def test_registry_rejects_threshold_mutation_after_activation(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    changed = PredictiveDriftEnvelope.create(
        strategy_id=envelope.strategy_id,
        definition_fingerprint=envelope.definition_fingerprint,
        source_identities=envelope.source_identities,
        metrics=(
            DriftMetricExpectation.create(
                metric_id="performance_return",
                direction=DriftDirection.LOWER_IS_WORSE,
                watch_boundary=Decimal("-0.10"),
                pause_boundary=Decimal("-0.30"),
                minimum_observations=1,
                window_sessions=126,
            ),
        ),
        activation_anchor=envelope.activation_anchor,
        checkpoint_interval_sessions=envelope.checkpoint_interval_sessions,
        bootstrap_seed=envelope.bootstrap_seed,
        bootstrap_repetitions=envelope.bootstrap_repetitions,
        bootstrap_block_sessions=envelope.bootstrap_block_sessions,
        frozen_at=envelope.frozen_at,
    )

    with pytest.raises(LiveDriftRegistryError, match="conflicts|thresholds"):
        registry.freeze_envelope(changed)


def test_definition_fingerprint_change_is_not_a_recovery_or_in_place_observation(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    changed = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint="b" * 64,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 20, 0, tzinfo=UTC),
        metrics=(
            DriftMetricObservation.create(
                metric_id="performance_return", value="0", sample_count=1
            ),
        ),
    )

    with pytest.raises(LiveDriftRegistryError, match="definition changed"):
        registry.record_observation(changed)


def test_general_recovery_requires_sessions_trades_guards_and_two_normal_checkpoints() -> None:
    envelope = _envelope()
    pause_observation = _observation(
        envelope,
        session=date(2026, 9, 8),
        value="-0.40",
    )
    pause = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(pause_observation,),
    )
    observations = [pause_observation]
    calendar = PrimaryUSSessionCalendar()
    for offset in range(1, 127):
        observations.append(
            _observation(
                envelope,
                session=calendar.session_offset(date(2026, 9, 8), offset),
                value="0",
            )
        )
    observations[-1] = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=observations[-1].session,
        observed_at=observations[-1].observed_at,
        metrics=observations[-1].metrics,
        completed_shadow_trades_total=6,
    )
    normal_two = evaluate_checkpoint(
        envelope,
        ordinal=2,
        session=date(2026, 10, 7),
        observations=tuple(observations),
        prior_state=pause.state,
        prior_watch_streak=pause.watch_streak,
    )
    normal_three = evaluate_checkpoint(
        envelope,
        ordinal=3,
        session=date(2026, 11, 5),
        observations=tuple(observations),
        prior_state=normal_two.state,
        prior_watch_streak=normal_two.watch_streak,
    )

    decision = evaluate_recovery(
        envelope,
        pause_checkpoint=pause,
        observations=tuple(observations),
        checkpoints=(pause, normal_two, normal_three),
        current_session=observations[-1].session,
        hard_guards_clear=True,
    )

    assert decision.eligible is True
    assert decision.recovery_kind == "general"
    assert decision.sessions_after_pause == 126
    assert decision.completed_shadow_trades_after_pause == 6


def test_data_ledger_only_recovery_uses_two_clean_checks_without_shadow_trades() -> None:
    envelope = _envelope()
    pause_observation = _observation(
        envelope,
        session=date(2026, 9, 8),
        value="0",
        guards=(
            HardGuardObservation.create(
                kind=HardGuardKind.RECONCILIATION,
                guard_id="reconciliation-current",
                active=True,
                evidence_identity="broker-1",
                reason="stale reconciliation",
            ),
        ),
    )
    pause = evaluate_checkpoint(
        envelope,
        ordinal=1,
        session=date(2026, 9, 8),
        observations=(pause_observation,),
    )
    decision = evaluate_recovery(
        envelope,
        pause_checkpoint=pause,
        observations=(pause_observation,),
        checkpoints=(pause,),
        current_session=date(2026, 9, 18),
        hard_guards_clear=True,
        cause_kinds=(HardGuardKind.RECONCILIATION,),
        clean_check_sessions=(date(2026, 9, 17), date(2026, 9, 18)),
    )

    assert decision.eligible is True
    assert decision.recovery_kind == "data_ledger_only"
    assert decision.completed_shadow_trades_after_pause == 0


def test_hard_guard_observation_pauses_before_a_scheduled_checkpoint(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    guard = HardGuardObservation.create(
        kind=HardGuardKind.DATA,
        guard_id="data-current",
        active=True,
        evidence_identity="bundle-1",
        reason="data is stale",
    )

    state = registry.record_observation(
        _observation(envelope, session=date(2026, 9, 8), guards=(guard,))
    )

    assert state.state is DriftState.PAUSED
    assert state.buy_allowed is False
    assert state.checkpoints == ()


def test_registry_rejects_out_of_order_sessions_and_replays_duplicate_idempotently(
    tmp_path,
) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    first = _observation(envelope, session=date(2026, 9, 8))
    registry.record_observation(first)
    assert registry.record_observation(first).observations == (first,)

    with pytest.raises(LiveDriftRegistryError, match="sessions must move forward"):
        registry.record_observation(_observation(envelope, session=date(2026, 9, 4)))
    with pytest.raises(LiveDriftRegistryError, match="sessions must move forward"):
        registry.record_observation(_observation(envelope, session=date(2026, 9, 8), value="-0.01"))


def test_data_guard_registry_recovery_requires_two_clean_checks(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(
        tmp_path / "live-drift.json",
        clean_check_verifier=lambda _session, _identity: True,
    )
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    active = HardGuardObservation.create(
        kind=HardGuardKind.RECONCILIATION,
        guard_id="reconciliation-current",
        active=True,
        evidence_identity="broker-1",
        reason="stale export",
    )
    clear = HardGuardObservation.create(
        kind=HardGuardKind.RECONCILIATION,
        guard_id="reconciliation-current",
        active=False,
        evidence_identity="broker-2",
        reason="reconciled",
    )
    registry.record_observation(_observation(envelope, session=date(2026, 9, 8), guards=(active,)))
    registry.record_observation(_observation(envelope, session=date(2026, 9, 9), guards=(clear,)))
    with pytest.raises(LiveDriftRegistryError, match="two distinct clean checks"):
        registry.recover(
            current_session=date(2026, 9, 9),
            cause_kinds=(HardGuardKind.RECONCILIATION,),
            hard_guards_clear=True,
            occurred_at=datetime(2026, 9, 9, 22, 0, tzinfo=UTC),
        )
    registry.record_clean_check(
        session=date(2026, 9, 10),
        evidence_identity="clean-1",
        occurred_at=datetime(2026, 9, 10, 21, 0, tzinfo=UTC),
    )
    registry.record_clean_check(
        session=date(2026, 9, 11),
        evidence_identity="clean-2",
        occurred_at=datetime(2026, 9, 11, 21, 0, tzinfo=UTC),
    )
    decision = registry.recover(
        current_session=date(2026, 9, 11),
        cause_kinds=(HardGuardKind.RECONCILIATION,),
        hard_guards_clear=True,
        occurred_at=datetime(2026, 9, 11, 21, 0, tzinfo=UTC),
    )

    assert decision.eligible is True
    assert registry.read().state is DriftState.HEALTHY

    registry.record_observation(_observation(envelope, session=date(2026, 9, 14), guards=(active,)))
    registry.record_observation(_observation(envelope, session=date(2026, 9, 15), guards=(clear,)))
    registry.record_clean_check(
        session=date(2026, 9, 16),
        evidence_identity="clean-3",
        occurred_at=datetime(2026, 9, 16, 21, 0, tzinfo=UTC),
    )
    registry.record_clean_check(
        session=date(2026, 9, 17),
        evidence_identity="clean-4",
        occurred_at=datetime(2026, 9, 17, 21, 0, tzinfo=UTC),
    )

    second_decision = registry.recover(
        current_session=date(2026, 9, 17),
        occurred_at=datetime(2026, 9, 17, 22, 0, tzinfo=UTC),
    )

    assert second_decision.eligible is True
    assert second_decision.clean_checks == 2


def test_recovery_cannot_claim_active_hard_guards_are_clear(tmp_path) -> None:
    envelope = _envelope()
    path = tmp_path / "live-drift.json"
    registry = LiveDriftRegistry(
        path,
        clean_check_verifier=lambda _session, _identity: True,
    )
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    active = HardGuardObservation.create(
        kind=HardGuardKind.RECONCILIATION,
        guard_id="reconciliation-current",
        active=True,
        evidence_identity="broker-1",
        reason="stale export",
    )
    registry.record_observation(
        DriftObservation.create(
            strategy_id=envelope.strategy_id,
            envelope_id=envelope.envelope_id,
            definition_fingerprint=envelope.definition_fingerprint,
            session=date(2026, 9, 8),
            observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
            metrics=(
                DriftMetricObservation.create(
                    metric_id="performance_return", value="0", sample_count=1
                ),
            ),
            hard_guards=(active,),
        )
    )
    for session in (date(2026, 9, 9), date(2026, 9, 10)):
        registry.record_clean_check(
            session=session,
            evidence_identity=session.isoformat(),
            occurred_at=datetime.combine(session, datetime.min.time(), tzinfo=UTC)
            + timedelta(hours=21),
        )
    before = registry.read()

    with pytest.raises(LiveDriftRegistryError, match="hard guards remain active"):
        registry.recover(
            current_session=date(2026, 9, 10),
            cause_kinds=(HardGuardKind.RECONCILIATION,),
            hard_guards_clear=True,
            occurred_at=datetime(2026, 9, 10, 22, 0, tzinfo=UTC),
        )

    after = registry.read()
    assert after.events == before.events
    assert after.state is DriftState.PAUSED


def test_mixed_pause_causes_cannot_be_narrowed_to_expedited_recovery(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(
        tmp_path / "live-drift.json",
        clean_check_verifier=lambda _session, _identity: True,
    )
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    active_guards = tuple(
        HardGuardObservation.create(
            kind=kind,
            guard_id=f"{kind.value}-current",
            active=True,
            evidence_identity=f"{kind.value}-1",
            reason="guard active",
        )
        for kind in (HardGuardKind.RECONCILIATION, HardGuardKind.EXECUTION)
    )
    clear_guards = tuple(
        HardGuardObservation.create(
            kind=guard.kind,
            guard_id=guard.guard_id,
            active=False,
            evidence_identity=f"{guard.kind.value}-2",
            reason="guard cleared",
        )
        for guard in active_guards
    )
    first = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
        metrics=(
            DriftMetricObservation.create(
                metric_id="performance_return", value="0", sample_count=1
            ),
        ),
        hard_guards=active_guards,
    )
    second = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 9),
        observed_at=datetime(2026, 9, 9, 21, 0, tzinfo=UTC),
        metrics=first.metrics,
        hard_guards=clear_guards,
    )
    registry.record_observation(first)
    registry.record_observation(second)
    for session in (date(2026, 9, 10), date(2026, 9, 11)):
        registry.record_clean_check(
            session=session,
            evidence_identity=session.isoformat(),
            occurred_at=datetime.combine(session, datetime.min.time(), tzinfo=UTC)
            + timedelta(hours=21),
        )

    with pytest.raises(LiveDriftRegistryError, match="exactly match"):
        registry.recover(
            current_session=date(2026, 9, 11),
            cause_kinds=(HardGuardKind.RECONCILIATION,),
            occurred_at=datetime(2026, 9, 11, 22, 0, tzinfo=UTC),
        )


def test_failed_semantic_append_is_not_published(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    frozen = registry.freeze_envelope(envelope)

    with pytest.raises(LiveDriftRegistryError, match="timestamp|completed"):
        registry.bind_activation(
            strategy_id=envelope.strategy_id,
            envelope_id=envelope.envelope_id,
            activation_event_id="activation-too-early",
            occurred_at=datetime(2026, 8, 6, 11, 0, tzinfo=UTC),
        )

    replayed = registry.read()
    assert replayed.events == frozen.events
    assert replayed.activation_event_id is None


def test_registry_rejects_session_not_completed_at_observation_time(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    future = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 12, 0, tzinfo=UTC),
        metrics=(
            DriftMetricObservation.create(
                metric_id="performance_return", value="0", sample_count=1
            ),
        ),
    )

    with pytest.raises(LiveDriftRegistryError, match="completed"):
        registry.record_observation(future)


def test_registry_rejects_unfrozen_metric_and_duplicate_guard_identity(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    unknown = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
        metrics=(DriftMetricObservation.create(metric_id="typo", value="0", sample_count=1),),
    )

    with pytest.raises(LiveDriftRegistryError, match="not frozen"):
        registry.record_observation(unknown)

    guard = HardGuardObservation.create(
        kind=HardGuardKind.DATA,
        guard_id="data-current",
        active=True,
        evidence_identity="bundle-1",
        reason="stale data",
    )
    with pytest.raises(ValueError, match="guard identities must be unique"):
        DriftObservation.create(
            strategy_id=envelope.strategy_id,
            envelope_id=envelope.envelope_id,
            definition_fingerprint=envelope.definition_fingerprint,
            session=date(2026, 9, 8),
            observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
            metrics=(
                DriftMetricObservation.create(
                    metric_id="performance_return", value="0", sample_count=1
                ),
            ),
            hard_guards=(guard, guard),
        )


def test_registry_rejects_unverified_shadow_trade_count(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    claimed = DriftObservation.create(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        definition_fingerprint=envelope.definition_fingerprint,
        session=date(2026, 9, 8),
        observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
        metrics=(
            DriftMetricObservation.create(
                metric_id="performance_return", value="0", sample_count=1
            ),
        ),
        completed_shadow_trades_total=6,
    )

    with pytest.raises(LiveDriftRegistryError, match="Shadow trade verifier"):
        registry.record_observation(claimed)


def test_checkpoint_and_recovery_dates_must_be_completed_sessions(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(
        tmp_path / "live-drift.json",
        clean_check_verifier=lambda _session, _identity: True,
        hard_guard_verifier=lambda: True,
    )
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    with pytest.raises(LiveDriftRegistryError, match="checkpoint session was not completed"):
        registry.record_checkpoint(
            ordinal=1,
            session=envelope.expected_checkpoint(1),
            evaluated_at=datetime(2026, 9, 8, 12, 0, tzinfo=UTC),
        )

    active = HardGuardObservation.create(
        kind=HardGuardKind.DATA,
        guard_id="data-current",
        active=True,
        evidence_identity="bundle-1",
        reason="stale data",
    )
    clear = HardGuardObservation.create(
        kind=HardGuardKind.DATA,
        guard_id="data-current",
        active=False,
        evidence_identity="bundle-2",
        reason="fresh data",
    )
    registry.record_observation(_observation(envelope, session=date(2026, 9, 8), guards=(active,)))
    registry.record_observation(_observation(envelope, session=date(2026, 9, 9), guards=(clear,)))
    for session in (date(2026, 9, 10), date(2026, 9, 11)):
        registry.record_clean_check(
            session=session,
            evidence_identity=session.isoformat(),
            occurred_at=datetime.combine(session, datetime.min.time(), tzinfo=UTC)
            + timedelta(hours=21),
        )

    with pytest.raises(LiveDriftRegistryError, match="recovery session was not completed"):
        registry.recover(
            current_session=date(2026, 9, 14),
            occurred_at=datetime(2026, 9, 13, 21, 0, tzinfo=UTC),
        )


def test_nested_strategy_registry_uses_manual_trading_coordination_root(tmp_path) -> None:
    registry = LiveDriftRegistry(tmp_path / "live-drift" / "spy.json")

    assert registry.coordination_lock_path == tmp_path / ".manual-trading-coordination.lock"


def test_clean_check_requires_a_trusted_reconciliation_verifier(tmp_path) -> None:
    envelope = _envelope()
    registry = LiveDriftRegistry(tmp_path / "live-drift.json")
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 10, 20, 0, tzinfo=UTC),
    )
    guard = HardGuardObservation.create(
        kind=HardGuardKind.LEDGER,
        guard_id="ledger-current",
        active=True,
        evidence_identity="ledger-1",
        reason="ledger verification failed",
    )
    registry.record_observation(
        DriftObservation.create(
            strategy_id=envelope.strategy_id,
            envelope_id=envelope.envelope_id,
            definition_fingerprint=envelope.definition_fingerprint,
            session=date(2026, 9, 8),
            observed_at=datetime(2026, 9, 8, 21, 0, tzinfo=UTC),
            metrics=(
                DriftMetricObservation.create(
                    metric_id="performance_return", value="0", sample_count=1
                ),
            ),
            hard_guards=(guard,),
        )
    )

    with pytest.raises(LiveDriftRegistryError, match="verifier is configured"):
        registry.record_clean_check(
            session=date(2026, 9, 9),
            evidence_identity="operator-assertion",
            occurred_at=datetime(2026, 9, 9, 21, 0, tzinfo=UTC),
        )


def test_registry_detects_deleted_history_and_manual_state_edits(tmp_path) -> None:
    envelope = _envelope()
    path = tmp_path / "live-drift.json"
    registry = LiveDriftRegistry(path)
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    registry.record_observation(_observation(envelope, session=date(2026, 9, 8)))
    tampered = json.loads(path.read_text(encoding="utf-8"))
    tampered["events"] = []
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(LiveDriftRegistryError, match="checkpoint"):
        registry.read()

    # Deleting the complete registry while retaining its private head must not look uninitialized.
    path.unlink()
    with pytest.raises(LiveDriftRegistryError, match="checkpoint exists"):
        registry.read()

    edited_path = tmp_path / "manually-edited-live-drift.json"
    edited_registry = LiveDriftRegistry(edited_path)
    edited_registry.freeze_envelope(envelope)
    edited_registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    edited_registry.record_observation(_observation(envelope, session=date(2026, 9, 8)))
    payload = json.loads(edited_path.read_text(encoding="utf-8"))
    payload["events"][0]["payload"]["strategy_id"] = "tampered"
    edited_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(LiveDriftRegistryError):
        edited_registry.read()


def test_concurrent_identical_append_is_idempotent_under_coordination_lock(tmp_path) -> None:
    envelope = _envelope()
    path = tmp_path / "live-drift.json"
    registry = LiveDriftRegistry(path)
    registry.freeze_envelope(envelope)
    registry.bind_activation(
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        activation_event_id="activation-1",
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
    )
    observation = _observation(envelope, session=date(2026, 9, 8))

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(registry.record_observation, (observation, observation)))

    assert all(result.observations == (observation,) for result in results)
    assert len(LiveDriftRegistry(path).read().events) == 3

"""Private append-only persistence for Phase 8 live-drift evidence."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from trading.core.accounting import canonical_json_bytes, parse_timestamp, timestamp_text
from trading.core.ledger_storage import atomic_write, locked_file
from trading.core.live_drift import (
    DRIFT_SCHEMA_VERSION,
    DriftAssessment,
    DriftCheckpoint,
    DriftError,
    DriftMetricExpectation,
    DriftMetricKind,
    DriftMetricObservation,
    DriftObservation,
    DriftState,
    HardGuardKind,
    HardGuardObservation,
    MetricAssessment,
    PredictiveDriftEnvelope,
    RecoveryDecision,
    evaluate_checkpoint,
    evaluate_recovery,
)
from trading.market_data import PrimaryUSSessionCalendar

_GENESIS_HASH = "0" * 64


class LiveDriftRegistryError(RuntimeError):
    """The live-drift history is malformed, conflicting, or unsafe."""


@dataclass(frozen=True, slots=True)
class LiveDriftState:
    """Verified projection of the private live-drift event history."""

    envelope: PredictiveDriftEnvelope | None
    activation_event_id: str | None
    state: DriftState
    watch_streak: int
    pause_session: date | None
    pause_cause_kinds: tuple[HardGuardKind, ...]
    observations: tuple[DriftObservation, ...]
    checkpoints: tuple[DriftCheckpoint, ...]
    recoveries: tuple[dict[str, object], ...]
    events: tuple[dict[str, object], ...]

    @property
    def buy_allowed(self) -> bool:
        """Return whether the Phase 8 overlay permits a new entry."""
        return self.envelope is not None and self.state is not DriftState.PAUSED

    @property
    def hard_guards(self) -> tuple[HardGuardObservation, ...]:
        """Return active latest hard guards from the verified observation stream."""
        latest: dict[tuple[HardGuardKind, str], HardGuardObservation] = {}
        for observation in self.observations:
            for guard in observation.hard_guards:
                latest[(guard.kind, guard.guard_id)] = guard
        return tuple(
            sorted(
                (guard for guard in latest.values() if guard.active),
                key=lambda item: (item.kind.value, item.guard_id),
            )
        )


class LiveDriftRegistry:
    """Append-only local authority for frozen drift expectations and recovery."""

    def __init__(
        self,
        path: Path,
        *,
        lock_timeout_seconds: float = 10.0,
        coordination_lock_path: Path | None = None,
        hard_guard_verifier: Callable[[], bool] | None = None,
        clean_check_verifier: Callable[[date, str], bool] | None = None,
        shadow_trade_verifier: Callable[[PredictiveDriftEnvelope, DriftObservation], bool]
        | None = None,
    ) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(f".{self.path.name}.lock")
        self.checkpoint_path = self.path.with_name(f".{self.path.name}.head.json")
        self.lock_timeout_seconds = lock_timeout_seconds
        coordination_root = (
            self.path.parent.parent if self.path.parent.name == "live-drift" else self.path.parent
        )
        self.coordination_lock_path = coordination_lock_path or (
            coordination_root / ".manual-trading-coordination.lock"
        )
        self.hard_guard_verifier = hard_guard_verifier
        self.clean_check_verifier = clean_check_verifier
        self.shadow_trade_verifier = shadow_trade_verifier

    def freeze_envelope(self, envelope: PredictiveDriftEnvelope) -> LiveDriftState:
        """Persist an envelope before activation; changed content is a conflict."""
        payload = envelope.payload()
        return self._append(
            event_id=f"envelope-frozen:{envelope.envelope_id}",
            event_type="drift_envelope_frozen",
            payload=payload,
            validator=lambda state: self._validate_envelope_append(state, envelope),
        )

    def bind_activation(
        self,
        *,
        strategy_id: str,
        envelope_id: str,
        activation_event_id: str,
        occurred_at: datetime,
    ) -> LiveDriftState:
        """Bind one frozen envelope to one Phase 7 activation event."""
        state = self.read()
        if state.envelope is None or state.envelope.envelope_id != envelope_id:
            raise LiveDriftRegistryError("activation references an unknown drift envelope")
        if state.envelope.strategy_id != strategy_id:
            raise LiveDriftRegistryError("activation strategy does not match drift envelope")
        timestamp = _timestamp_text(occurred_at, "activation timestamp")
        payload = {
            "strategy_id": strategy_id,
            "envelope_id": envelope_id,
            "activation_event_id": _required_text(activation_event_id, "activation_event_id"),
            "occurred_at": timestamp,
        }
        return self._append(
            event_id=f"activation-bound:{activation_event_id}",
            event_type="drift_activation_bound",
            payload=payload,
            validator=lambda current: self._validate_activation_append(
                current, strategy_id, envelope_id, activation_event_id
            ),
        )

    def record_observation(self, observation: DriftObservation) -> LiveDriftState:
        """Append one monotonic completed-session observation."""
        state = self.read()
        self._require_bound_observation(state, observation)
        payload = observation.payload()
        return self._append(
            event_id=f"observation:{observation.observation_id}",
            event_type="live_observation_recorded",
            payload=payload,
            validator=lambda current: self._validate_observation_append(current, observation),
        )

    def record_checkpoint(
        self,
        *,
        ordinal: int,
        session: date,
        evaluated_at: datetime | None = None,
    ) -> DriftCheckpoint:
        """Recompute and append one scheduled checkpoint from registry history."""
        state = self.read()
        envelope = self._require_envelope(state)
        prior = state.checkpoints[-1] if state.checkpoints else None
        checkpoint = evaluate_checkpoint(
            envelope,
            ordinal=ordinal,
            session=session,
            observations=state.observations,
            prior_state=prior.state if prior is not None else DriftState.HEALTHY,
            prior_watch_streak=prior.watch_streak if prior is not None else 0,
        )
        checkpoint_timestamp = evaluated_at or max(
            (observation.observed_at for observation in state.observations),
            default=envelope.frozen_at,
        )
        if _latest_completed_session(checkpoint_timestamp, "checkpoint timestamp") < session:
            raise LiveDriftRegistryError(
                "checkpoint session was not completed at the evaluation timestamp"
            )
        payload = {
            **checkpoint.payload(),
            "evaluated_at": _timestamp_text(checkpoint_timestamp, "checkpoint timestamp"),
        }
        self._append(
            event_id=f"checkpoint:{checkpoint.checkpoint_id}",
            event_type="drift_checkpoint_evaluated",
            payload=payload,
            validator=lambda current: self._validate_checkpoint_append(current, checkpoint),
        )
        return checkpoint

    def record_clean_check(
        self,
        *,
        session: date,
        evidence_identity: str,
        occurred_at: datetime,
    ) -> LiveDriftState:
        """Record one distinct verified integrity check for expedited recovery."""
        if self.clean_check_verifier is None:
            raise LiveDriftRegistryError(
                "clean checks require a trusted reconciliation verifier is configured"
            )
        payload = {
            "session": _date_text(session, "clean check session"),
            "evidence_identity": _required_text(evidence_identity, "evidence_identity"),
            "occurred_at": _timestamp_text(occurred_at, "clean check timestamp"),
        }
        if not self.clean_check_verifier(session, evidence_identity):
            raise LiveDriftRegistryError("clean check verifier did not confirm reconciliation")
        event_id = "clean-check:" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        return self._append(
            event_id=event_id,
            event_type="clean_check_recorded",
            payload=payload,
            validator=lambda state: self._validate_clean_check_append(state, payload),
        )

    def recover(
        self,
        *,
        current_session: date,
        cause_kinds: Sequence[HardGuardKind] = (),
        clean_check_sessions: Sequence[date] = (),
        hard_guards_clear: bool | None = None,
        occurred_at: datetime | None = None,
    ) -> RecoveryDecision:
        """Append a recovery only when the replayed evidence recomputes as eligible."""
        state = self.read()
        envelope = self._require_envelope(state)
        pause_checkpoint = self._latest_pause_checkpoint(state)
        if pause_checkpoint is None and state.pause_session is None:
            raise LiveDriftRegistryError("recovery requires a persisted pause evidence")
        recorded_clean_checks = self._clean_check_sessions(
            state,
            after=state.pause_session,
        )
        requested_clean_checks = tuple(sorted(set(clean_check_sessions)))
        if requested_clean_checks and not set(requested_clean_checks).issubset(
            set(recorded_clean_checks)
        ):
            raise LiveDriftRegistryError("recovery clean checks are not recorded evidence")
        requested_causes = tuple(sorted(set(HardGuardKind(kind) for kind in cause_kinds)))
        if requested_causes and set(requested_causes) != set(state.pause_cause_kinds):
            raise LiveDriftRegistryError(
                "recovery causes must exactly match the recorded pause evidence"
            )
        actual_causes = requested_causes or state.pause_cause_kinds
        metric_pause = pause_checkpoint is not None and any(
            item.assessment is DriftAssessment.PAUSED
            for item in pause_checkpoint.metric_assessments
        )
        if metric_pause and all(
            HardGuardKind(kind)
            in {HardGuardKind.DATA, HardGuardKind.LEDGER, HardGuardKind.RECONCILIATION}
            for kind in actual_causes
        ):
            actual_causes = ()
        persisted_guards_clear = not state.hard_guards
        caller_did_not_block = hard_guards_clear is not False
        hard_guards_clear = persisted_guards_clear and caller_did_not_block
        if self.hard_guard_verifier is not None:
            hard_guards_clear = bool(self.hard_guard_verifier()) and hard_guards_clear
        recovery_timestamp = occurred_at or datetime.now(UTC)
        if not _is_xnys_session(current_session):
            raise LiveDriftRegistryError("recovery current session is not an XNYS session")
        if _latest_completed_session(recovery_timestamp, "recovery timestamp") < current_session:
            raise LiveDriftRegistryError(
                "recovery session was not completed at the recovery timestamp"
            )
        decision = evaluate_recovery(
            envelope,
            pause_checkpoint=pause_checkpoint,
            pause_session=state.pause_session if pause_checkpoint is None else None,
            pause_completed_shadow_trades_total=(
                self._pause_shadow_trade_total(state) if pause_checkpoint is None else 0
            ),
            observations=state.observations,
            checkpoints=state.checkpoints,
            current_session=current_session,
            hard_guards_clear=bool(hard_guards_clear),
            cause_kinds=actual_causes,
            clean_check_sessions=requested_clean_checks or recorded_clean_checks,
        )
        if not decision.eligible:
            raise LiveDriftRegistryError("recovery gate failed: " + "; ".join(decision.reasons))
        payload = {
            "envelope_id": envelope.envelope_id,
            "pause_checkpoint_id": (
                pause_checkpoint.checkpoint_id if pause_checkpoint is not None else None
            ),
            "pause_session": (
                pause_checkpoint.session.isoformat()
                if pause_checkpoint is not None
                else state.pause_session.isoformat()
                if state.pause_session is not None
                else None
            ),
            "current_session": _date_text(current_session, "recovery current session"),
            "recovery_kind": decision.recovery_kind,
            "sessions_after_pause": decision.sessions_after_pause,
            "completed_shadow_trades_after_pause": decision.completed_shadow_trades_after_pause,
            "normal_checkpoints": decision.normal_checkpoints,
            "clean_checks": decision.clean_checks,
            "cause_kinds": sorted(HardGuardKind(kind).value for kind in actual_causes),
            "occurred_at": _timestamp_text(recovery_timestamp, "recovery timestamp"),
        }
        self._append(
            event_id="recovery:" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
            event_type="drift_recovery_evaluated",
            payload=payload,
            validator=lambda current: self._validate_recovery_append(current, decision),
        )
        return decision

    def read(self) -> LiveDriftState:
        """Read and replay the verified registry under both coordination and registry locks."""
        with locked_file(self.coordination_lock_path, self.lock_timeout_seconds):
            with locked_file(self.lock_path, self.lock_timeout_seconds):
                return self._project(self._load_unlocked(allow_missing=True))

    def read_while_coordinated(self) -> LiveDriftState:
        """Read while the caller already holds ``coordination_lock_path`` exclusively."""
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            return self._project(self._load_unlocked(allow_missing=True))

    def _append(
        self,
        *,
        event_id: str,
        event_type: str,
        payload: dict[str, object],
        validator: Callable[[LiveDriftState], None] | None = None,
    ) -> LiveDriftState:
        with locked_file(self.coordination_lock_path, self.lock_timeout_seconds):
            with locked_file(self.lock_path, self.lock_timeout_seconds):
                state = self._load_unlocked(allow_missing=True)
                projected = self._project(state)
                existing = next(
                    (event for event in _events(state) if event.get("event_id") == event_id),
                    None,
                )
                if existing is not None:
                    if (
                        existing.get("event_type") != event_type
                        or existing.get("payload") != payload
                    ):
                        raise LiveDriftRegistryError(f"event {event_id} conflicts with history")
                    return projected
                if validator is not None:
                    validator(projected)
                events = _events(state)
                previous_hash = events[-1]["event_hash"] if events else _GENESIS_HASH
                content = {
                    "sequence": len(events) + 1,
                    "event_id": event_id,
                    "event_type": event_type,
                    "payload": payload,
                    "previous_hash": previous_hash,
                }
                events.append(
                    {
                        **content,
                        "event_hash": hashlib.sha256(canonical_json_bytes(content)).hexdigest(),
                    }
                )
                candidate = self._project(state)
                self._publish(state)
                return candidate

    def _load_unlocked(self, *, allow_missing: bool) -> dict[str, object]:
        if not self.path.exists():
            if self.checkpoint_path.exists():
                raise LiveDriftRegistryError(
                    "live-drift registry is missing but its head checkpoint exists"
                )
            if allow_missing:
                return {"schema_version": DRIFT_SCHEMA_VERSION, "events": []}
            raise LiveDriftRegistryError("live-drift registry is not initialized")
        try:
            content = self.path.read_bytes()
            state = json.loads(content)
        except (OSError, json.JSONDecodeError) as exc:
            raise LiveDriftRegistryError(f"live-drift registry cannot be read: {exc}") from exc
        if not isinstance(state, dict) or state.get("schema_version") != DRIFT_SCHEMA_VERSION:
            raise LiveDriftRegistryError("live-drift registry has an unsupported schema")
        events = _events(state)
        _validate_hash_chain(events)
        _verify_checkpoint(self.checkpoint_path, content, events)
        return state

    def _publish(self, state: dict[str, object]) -> None:
        content = canonical_json_bytes(state)
        atomic_write(self.path, content, replace=True)
        events = _events(state)
        checkpoint = {
            "schema_version": DRIFT_SCHEMA_VERSION,
            "event_count": len(events),
            "registry_checksum": hashlib.sha256(content).hexdigest(),
            "head_hash": events[-1]["event_hash"] if events else _GENESIS_HASH,
        }
        atomic_write(self.checkpoint_path, canonical_json_bytes(checkpoint), replace=True)

    def _project(self, state: dict[str, object]) -> LiveDriftState:
        events = _events(state)
        envelope: PredictiveDriftEnvelope | None = None
        activation_event_id: str | None = None
        observations: list[DriftObservation] = []
        checkpoints: list[DriftCheckpoint] = []
        recoveries: list[dict[str, object]] = []
        state_value = DriftState.HEALTHY
        watch_streak = 0
        pause_session: date | None = None
        pause_cause_kinds: set[HardGuardKind] = set()
        previous_session: date | None = None
        previous_observed_at: datetime | None = None
        previous_ordinal = 0
        previous_event_at: datetime | None = None
        for event_index, event in enumerate(events):
            event_type = event["event_type"]
            payload = event["payload"]
            event_at = _event_timestamp(event_type, payload)
            if previous_event_at is not None and event_at < previous_event_at:
                raise LiveDriftRegistryError("live-drift event timestamps moved backward")
            previous_event_at = event_at
            if event_type == "drift_envelope_frozen":
                candidate = _envelope_from_payload(payload)
                if envelope is not None and envelope != candidate:
                    raise LiveDriftRegistryError("multiple drift envelopes are not supported")
                envelope = candidate
            elif event_type == "drift_activation_bound":
                if envelope is None or payload.get("envelope_id") != envelope.envelope_id:
                    raise LiveDriftRegistryError("activation is not bound to the frozen envelope")
                if payload.get("strategy_id") != envelope.strategy_id:
                    raise LiveDriftRegistryError(
                        "activation strategy is not bound to the frozen envelope"
                    )
                if set(payload) != {
                    "strategy_id",
                    "envelope_id",
                    "activation_event_id",
                    "occurred_at",
                }:
                    raise LiveDriftRegistryError("activation payload is not canonical")
                _required_text(payload.get("activation_event_id"), "activation_event_id")
                if activation_event_id is not None and activation_event_id != payload.get(
                    "activation_event_id"
                ):
                    raise LiveDriftRegistryError("activation binding conflicts with history")
                activation_event_id = str(payload["activation_event_id"])
            elif event_type == "live_observation_recorded":
                observation = _observation_from_payload(payload)
                if envelope is None or observation.envelope_id != envelope.envelope_id:
                    raise LiveDriftRegistryError("observation is not bound to the frozen envelope")
                if activation_event_id is None:
                    raise LiveDriftRegistryError("observation precedes activation binding")
                _validate_observation_against_envelope(envelope, observation)
                if previous_session is not None and observation.session < previous_session:
                    raise LiveDriftRegistryError("observation sessions moved backward")
                if observation.session == previous_session:
                    raise LiveDriftRegistryError("duplicate observation session is not allowed")
                if (
                    previous_observed_at is not None
                    and observation.observed_at < previous_observed_at
                ):
                    raise LiveDriftRegistryError("observation timestamps moved backward")
                previous_session = observation.session
                previous_observed_at = observation.observed_at
                observations.append(observation)
                for guard in observation.hard_guards:
                    if guard.active:
                        state_value = DriftState.PAUSED
                        pause_session = pause_session or observation.session
                        pause_cause_kinds.add(guard.kind)
            elif event_type == "drift_checkpoint_evaluated":
                checkpoint = _checkpoint_from_payload(payload)
                if envelope is None or checkpoint.envelope_id != envelope.envelope_id:
                    raise LiveDriftRegistryError("checkpoint is not bound to the frozen envelope")
                if checkpoint.strategy_id != envelope.strategy_id:
                    raise LiveDriftRegistryError(
                        "checkpoint strategy is not bound to the frozen envelope"
                    )
                if checkpoint.session != envelope.expected_checkpoint(checkpoint.ordinal):
                    raise LiveDriftRegistryError(
                        "checkpoint session is outside the frozen schedule"
                    )
                if _latest_completed_session(event_at, "checkpoint timestamp") < checkpoint.session:
                    raise LiveDriftRegistryError(
                        "checkpoint session was not completed at the evaluation timestamp"
                    )
                if checkpoint.ordinal != previous_ordinal + 1:
                    raise LiveDriftRegistryError("checkpoint ordinals must be contiguous")
                if observations and observations[-1].session > checkpoint.session:
                    raise LiveDriftRegistryError(
                        "checkpoint session precedes the latest recorded observation"
                    )
                expected_checkpoint = evaluate_checkpoint(
                    envelope,
                    ordinal=checkpoint.ordinal,
                    session=checkpoint.session,
                    observations=tuple(observations),
                    prior_state=checkpoints[-1].state if checkpoints else DriftState.HEALTHY,
                    prior_watch_streak=checkpoints[-1].watch_streak if checkpoints else 0,
                )
                if expected_checkpoint != checkpoint:
                    raise LiveDriftRegistryError("checkpoint is not a deterministic replay result")
                if payload != {
                    **checkpoint.payload(),
                    "evaluated_at": payload.get("evaluated_at"),
                }:
                    raise LiveDriftRegistryError("checkpoint payload is not canonical")
                previous_ordinal = checkpoint.ordinal
                checkpoints.append(checkpoint)
                state_value = checkpoint.state
                watch_streak = checkpoint.watch_streak
                if checkpoint.state is DriftState.PAUSED:
                    pause_session = pause_session or checkpoint.session
                    pause_cause_kinds.update(guard.kind for guard in checkpoint.active_hard_guards)
            elif event_type == "clean_check_recorded":
                if set(payload) != {"session", "evidence_identity", "occurred_at"}:
                    raise LiveDriftRegistryError("clean check payload is not canonical")
                _validate_clean_payload(payload)
                clean_session = date.fromisoformat(str(payload["session"]))
                if pause_session is None:
                    raise LiveDriftRegistryError("clean check has no replayable pause evidence")
                if clean_session <= pause_session or not _is_xnys_session(clean_session):
                    raise LiveDriftRegistryError("clean check session is outside the pause window")
                if _latest_completed_session(event_at, "clean check timestamp") < clean_session:
                    raise LiveDriftRegistryError(
                        "clean check session was not completed at its timestamp"
                    )
            elif event_type == "drift_recovery_evaluated":
                if envelope is None:
                    raise LiveDriftRegistryError("recovery is not bound to an envelope")
                if set(payload) != {
                    "envelope_id",
                    "pause_checkpoint_id",
                    "pause_session",
                    "current_session",
                    "recovery_kind",
                    "sessions_after_pause",
                    "completed_shadow_trades_after_pause",
                    "normal_checkpoints",
                    "clean_checks",
                    "cause_kinds",
                    "occurred_at",
                }:
                    raise LiveDriftRegistryError("recovery payload is not canonical")
                if payload.get("envelope_id") != envelope.envelope_id:
                    raise LiveDriftRegistryError("recovery envelope does not match history")
                pause_checkpoint = next(
                    (
                        item
                        for item in reversed(checkpoints)
                        if item.state is DriftState.PAUSED
                        and (pause_session is None or item.session >= pause_session)
                    ),
                    None,
                )
                recovery_causes = tuple(
                    HardGuardKind(str(value)) for value in payload.get("cause_kinds", ())
                )
                if pause_checkpoint is not None and any(
                    item.assessment is DriftAssessment.PAUSED
                    for item in pause_checkpoint.metric_assessments
                ):
                    recovery_causes = ()
                try:
                    current_session = date.fromisoformat(str(payload["current_session"]))
                    recovery_pause_session = (
                        pause_checkpoint.session if pause_checkpoint is not None else pause_session
                    )
                    clean_sessions = tuple(
                        sorted(
                            clean_session
                            for item in events[:event_index]
                            if item.get("event_type") == "clean_check_recorded"
                            for clean_session in (
                                date.fromisoformat(str(item["payload"]["session"])),
                            )
                            if recovery_pause_session is not None
                            and clean_session > recovery_pause_session
                        )
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    raise LiveDriftRegistryError("recovery payload is malformed") from exc
                if (
                    not _is_xnys_session(current_session)
                    or _latest_completed_session(event_at, "recovery timestamp") < current_session
                ):
                    raise LiveDriftRegistryError("recovery current session is not completed")
                if pause_checkpoint is None and pause_session is None:
                    raise LiveDriftRegistryError("recovery has no replayable pause evidence")
                latest_guard_values: dict[tuple[HardGuardKind, str], HardGuardObservation] = {}
                for item in observations:
                    for guard in item.hard_guards:
                        latest_guard_values[(guard.kind, guard.guard_id)] = guard
                replay_decision = evaluate_recovery(
                    envelope,
                    pause_checkpoint=pause_checkpoint,
                    pause_session=pause_session if pause_checkpoint is None else None,
                    pause_completed_shadow_trades_total=(
                        max(
                            (
                                item.completed_shadow_trades_total
                                for item in observations
                                if pause_session is not None and item.session <= pause_session
                            ),
                            default=0,
                        )
                        if pause_checkpoint is None
                        else 0
                    ),
                    observations=tuple(observations),
                    checkpoints=tuple(checkpoints),
                    current_session=current_session,
                    hard_guards_clear=not any(
                        guard.active for guard in latest_guard_values.values()
                    ),
                    cause_kinds=recovery_causes,
                    clean_check_sessions=clean_sessions,
                )
                if (
                    not replay_decision.eligible
                    or payload.get("recovery_kind") != replay_decision.recovery_kind
                    or payload.get("sessions_after_pause") != replay_decision.sessions_after_pause
                    or payload.get("completed_shadow_trades_after_pause")
                    != replay_decision.completed_shadow_trades_after_pause
                    or payload.get("normal_checkpoints") != replay_decision.normal_checkpoints
                    or payload.get("clean_checks") != replay_decision.clean_checks
                ):
                    raise LiveDriftRegistryError(
                        "recovery event is not a deterministic replay result"
                    )
                recoveries.append(copy.deepcopy(payload))
                state_value = DriftState.HEALTHY
                watch_streak = 0
                pause_session = None
                pause_cause_kinds.clear()
            else:
                raise LiveDriftRegistryError(f"unknown live-drift event: {event_type}")
        if envelope is None or activation_event_id is None:
            state_value = DriftState.PAUSED
        elif pause_session is not None:
            state_value = DriftState.PAUSED
        if observations:
            latest_guards: dict[tuple[HardGuardKind, str], HardGuardObservation] = {}
            for observation in observations:
                for guard in observation.hard_guards:
                    latest_guards[(guard.kind, guard.guard_id)] = guard
            if any(guard.active for guard in latest_guards.values()):
                state_value = DriftState.PAUSED
        return LiveDriftState(
            envelope=envelope,
            activation_event_id=activation_event_id,
            state=state_value,
            watch_streak=watch_streak,
            pause_session=pause_session,
            pause_cause_kinds=tuple(sorted(pause_cause_kinds, key=lambda item: item.value)),
            observations=tuple(observations),
            checkpoints=tuple(checkpoints),
            recoveries=tuple(recoveries),
            events=tuple(copy.deepcopy(events)),
        )

    def _validate_envelope_append(
        self, state: LiveDriftState, envelope: PredictiveDriftEnvelope
    ) -> None:
        if state.envelope is not None and state.envelope != envelope:
            raise LiveDriftRegistryError("frozen drift envelope conflicts with history")
        if state.activation_event_id is not None:
            raise LiveDriftRegistryError("thresholds cannot change after activation")

    def _validate_activation_append(
        self,
        state: LiveDriftState,
        strategy_id: str,
        envelope_id: str,
        activation_event_id: str,
    ) -> None:
        if state.envelope is None or state.envelope.envelope_id != envelope_id:
            raise LiveDriftRegistryError("activation envelope is missing")
        if state.envelope.strategy_id != strategy_id:
            raise LiveDriftRegistryError("activation strategy conflicts with envelope")
        if (
            state.activation_event_id is not None
            and state.activation_event_id != activation_event_id
        ):
            raise LiveDriftRegistryError("activation binding conflicts with history")

    def _require_bound_observation(
        self, state: LiveDriftState, observation: DriftObservation
    ) -> None:
        if state.envelope is None or state.activation_event_id is None:
            raise LiveDriftRegistryError("observations require a bound active envelope")
        if observation.envelope_id != state.envelope.envelope_id:
            raise LiveDriftRegistryError("observation envelope does not match frozen envelope")
        if observation.strategy_id != state.envelope.strategy_id:
            raise LiveDriftRegistryError("observation strategy does not match frozen envelope")
        if observation.definition_fingerprint != state.envelope.definition_fingerprint:
            raise LiveDriftRegistryError("observation definition changed frozen envelope")
        _validate_observation_against_envelope(state.envelope, observation)
        if observation.completed_shadow_trades_total > 0:
            if self.shadow_trade_verifier is None:
                raise LiveDriftRegistryError(
                    "completed Shadow trades require a trusted Shadow trade verifier"
                )
            if not self.shadow_trade_verifier(state.envelope, observation):
                raise LiveDriftRegistryError(
                    "Shadow trade verifier did not confirm the observation"
                )

    def _validate_observation_append(
        self, state: LiveDriftState, observation: DriftObservation
    ) -> None:
        self._require_bound_observation(state, observation)
        if state.observations and observation.session <= state.observations[-1].session:
            raise LiveDriftRegistryError("observation sessions must move forward")

    def _validate_checkpoint_append(
        self, state: LiveDriftState, checkpoint: DriftCheckpoint
    ) -> None:
        envelope = self._require_envelope(state)
        expected = evaluate_checkpoint(
            envelope,
            ordinal=checkpoint.ordinal,
            session=checkpoint.session,
            observations=state.observations,
            prior_state=state.checkpoints[-1].state if state.checkpoints else DriftState.HEALTHY,
            prior_watch_streak=state.checkpoints[-1].watch_streak if state.checkpoints else 0,
        )
        if expected != checkpoint:
            raise LiveDriftRegistryError("checkpoint payload is not the recomputed result")
        if state.observations and state.observations[-1].session > checkpoint.session:
            raise LiveDriftRegistryError(
                "checkpoint session precedes the latest recorded observation"
            )
        if state.checkpoints and checkpoint.ordinal != state.checkpoints[-1].ordinal + 1:
            raise LiveDriftRegistryError("checkpoint ordinals must be contiguous")

    def _validate_clean_check_append(
        self, state: LiveDriftState, payload: Mapping[str, object]
    ) -> None:
        if state.state is not DriftState.PAUSED:
            raise LiveDriftRegistryError("clean checks require a paused strategy")
        _validate_clean_payload(payload)
        session = date.fromisoformat(str(payload["session"]))
        if state.pause_session is None or session <= state.pause_session:
            raise LiveDriftRegistryError("clean checks must follow the pause session")
        if not _is_xnys_session(session):
            raise LiveDriftRegistryError("clean check session is not an XNYS session")
        occurred_at = parse_timestamp(str(payload["occurred_at"]))
        if _latest_completed_session(occurred_at, "clean check timestamp") < session:
            raise LiveDriftRegistryError("clean check session was not completed at its timestamp")
        if session in self._clean_check_sessions(state):
            raise LiveDriftRegistryError("clean check sessions must be distinct")

    def _validate_recovery_append(self, state: LiveDriftState, decision: RecoveryDecision) -> None:
        if state.state is not DriftState.PAUSED or not decision.eligible:
            raise LiveDriftRegistryError("recovery is not eligible from current state")

    def _require_envelope(self, state: LiveDriftState) -> PredictiveDriftEnvelope:
        if state.envelope is None:
            raise LiveDriftRegistryError("drift envelope is not frozen")
        return state.envelope

    def _latest_pause_checkpoint(self, state: LiveDriftState) -> DriftCheckpoint | None:
        for checkpoint in reversed(state.checkpoints):
            if checkpoint.state is DriftState.PAUSED and (
                state.pause_session is None or checkpoint.session >= state.pause_session
            ):
                return checkpoint
        return None

    @staticmethod
    def _pause_shadow_trade_total(state: LiveDriftState) -> int:
        if state.pause_session is None:
            return 0
        return max(
            (
                observation.completed_shadow_trades_total
                for observation in state.observations
                if observation.session <= state.pause_session
            ),
            default=0,
        )

    @staticmethod
    def _clean_check_sessions(
        state: LiveDriftState,
        *,
        after: date | None = None,
    ) -> tuple[date, ...]:
        return tuple(
            sorted(
                session
                for event in state.events
                if event.get("event_type") == "clean_check_recorded"
                for session in (date.fromisoformat(str(event["payload"]["session"])),)
                if after is None or session > after
            )
        )


def verify_envelope_qualification_sources(
    envelope: PredictiveDriftEnvelope,
    *,
    qualification_state: Mapping[str, object],
    shadow_id: str,
    activation_event_id: str,
) -> None:
    """Bind a frozen envelope to exact verified Historical Screen and Shadow events."""
    events = qualification_state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, Mapping) for event in events):
        raise LiveDriftRegistryError("qualification source history is malformed")

    def event_for(event_id: str) -> Mapping[str, object]:
        event = next((item for item in events if item.get("event_id") == event_id), None)
        if event is None:
            raise LiveDriftRegistryError(f"qualification source event is missing: {event_id}")
        return event

    registration = event_for(f"shadow-registration:{shadow_id}")
    registration_payload = registration.get("payload")
    activation = event_for(activation_event_id)
    activation_payload = activation.get("payload")
    if (
        registration.get("event_type") != "shadow_registration"
        or not isinstance(registration_payload, Mapping)
        or registration_payload.get("shadow_id") != shadow_id
        or registration_payload.get("definition_fingerprint") != envelope.definition_fingerprint
        or activation.get("event_type") != "activation_evaluation"
        or not isinstance(activation_payload, Mapping)
        or activation_payload.get("shadow_id") != shadow_id
        or activation_payload.get("eligible") is not True
        or activation_payload.get("disposition") != "activation-eligible"
    ):
        raise LiveDriftRegistryError(
            "predictive envelope does not match eligible Shadow qualification"
        )
    plan_id = registration_payload.get("historical_plan_id")
    evaluated_at = activation_payload.get("evaluated_at")
    if not isinstance(plan_id, str) or not plan_id or not isinstance(evaluated_at, str):
        raise LiveDriftRegistryError("qualification source identities are malformed")
    try:
        source_session = date.fromisoformat(evaluated_at)
    except ValueError as exc:
        raise LiveDriftRegistryError("qualification source date is malformed") from exc
    if envelope.frozen_at.date() < source_session:
        raise LiveDriftRegistryError(
            "predictive envelope cannot be frozen before its Shadow source evidence"
        )
    screen_id = f"historical-screen:{plan_id}"
    evidence_id = f"shadow-evidence:{shadow_id}:{evaluated_at}"
    screen = event_for(screen_id)
    evidence = event_for(evidence_id)
    screen_payload = screen.get("payload")
    evidence_payload = evidence.get("payload")
    if (
        screen.get("event_type") != "historical_screen"
        or not isinstance(screen_payload, Mapping)
        or screen_payload.get("plan_id") != plan_id
        or screen_payload.get("passed") is not True
        or evidence.get("event_type") != "shadow_evidence"
        or not isinstance(evidence_payload, Mapping)
        or evidence_payload.get("shadow_id") != shadow_id
        or evidence_payload.get("definition_fingerprint") != envelope.definition_fingerprint
        or evidence_payload.get("as_of") != evaluated_at
        or not isinstance(evidence_payload.get("simulated_fills"), list)
    ):
        raise LiveDriftRegistryError("predictive envelope qualification sources are invalid")
    if set(envelope.source_identities) != {screen_id, evidence_id}:
        raise LiveDriftRegistryError(
            "predictive envelope source identities must exactly match Historical and Shadow evidence"
        )
    required_metric_kinds = {
        DriftMetricKind.PERFORMANCE,
        DriftMetricKind.SIGNAL,
        DriftMetricKind.EXECUTION,
        DriftMetricKind.UTILIZATION,
        DriftMetricKind.CONCENTRATION,
    }
    missing_metric_kinds = required_metric_kinds - {metric.kind for metric in envelope.metrics}
    if missing_metric_kinds:
        missing = ", ".join(sorted(kind.value for kind in missing_metric_kinds))
        raise LiveDriftRegistryError(
            f"predictive envelope is missing required metric families: {missing}"
        )


def verified_shadow_trade_total(
    envelope: PredictiveDriftEnvelope,
    *,
    qualification_state: Mapping[str, object],
    evidence_event_id: str,
    session: date,
) -> int:
    """Return the verified cumulative simulated-fill count for one live observation session."""
    events = qualification_state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, Mapping) for event in events):
        raise LiveDriftRegistryError("qualification source history is malformed")
    event = next((item for item in events if item.get("event_id") == evidence_event_id), None)
    payload = event.get("payload") if event is not None else None
    if (
        event is None
        or event.get("event_type") != "shadow_evidence"
        or not isinstance(payload, Mapping)
        or payload.get("definition_fingerprint") != envelope.definition_fingerprint
        or payload.get("as_of") != session.isoformat()
        or not isinstance(payload.get("shadow_id"), str)
        or not isinstance(payload.get("simulated_fills"), list)
    ):
        raise LiveDriftRegistryError("Shadow observation evidence is missing or incompatible")
    shadow_prefix = f"shadow-evidence:{payload['shadow_id']}:"
    if not any(source.startswith(shadow_prefix) for source in envelope.source_identities):
        raise LiveDriftRegistryError("Shadow observation belongs to a different frozen source")
    if evidence_event_id != f"{shadow_prefix}{session.isoformat()}":
        raise LiveDriftRegistryError("Shadow observation evidence identity is not canonical")
    return len(payload["simulated_fills"])


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LiveDriftRegistryError(f"{field} must be a non-empty string")
    return value.strip()


def _date_text(value: date, field: str) -> str:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise LiveDriftRegistryError(f"{field} must be a date")
    return value.isoformat()


def _is_xnys_session(value: date) -> bool:
    try:
        return PrimaryUSSessionCalendar().session_on_or_before(value) == value
    except (TypeError, ValueError):
        return False


def _latest_completed_session(value: datetime, field: str) -> date:
    try:
        return PrimaryUSSessionCalendar().latest_completed_session(value)
    except (TypeError, ValueError) as exc:
        raise LiveDriftRegistryError(f"{field} cannot be verified") from exc


def _validate_observation_against_envelope(
    envelope: PredictiveDriftEnvelope,
    observation: DriftObservation,
) -> None:
    if observation.strategy_id != envelope.strategy_id:
        raise LiveDriftRegistryError("observation strategy does not match frozen envelope")
    if observation.definition_fingerprint != envelope.definition_fingerprint:
        raise LiveDriftRegistryError("observation definition changed frozen envelope")
    if observation.session <= envelope.activation_anchor:
        raise LiveDriftRegistryError("observation must follow activation anchor")
    if not _is_xnys_session(observation.session):
        raise LiveDriftRegistryError("observation session is not a completed XNYS session")
    if (
        _latest_completed_session(observation.observed_at, "observation timestamp")
        < observation.session
    ):
        raise LiveDriftRegistryError(
            "observation session was not completed at the observation timestamp"
        )
    frozen_metric_ids = {metric.metric_id for metric in envelope.metrics}
    unexpected_metric = next(
        (
            metric.metric_id
            for metric in observation.metrics
            if metric.metric_id not in frozen_metric_ids
        ),
        None,
    )
    if unexpected_metric is not None:
        raise LiveDriftRegistryError(
            f"observation metric is not frozen in envelope: {unexpected_metric}"
        )
    frozen_guard_kinds = set(envelope.hard_guard_kinds)
    unexpected_guard = next(
        (guard.kind for guard in observation.hard_guards if guard.kind not in frozen_guard_kinds),
        None,
    )
    if unexpected_guard is not None:
        raise LiveDriftRegistryError(
            f"hard-guard kind is not frozen in envelope: {unexpected_guard.value}"
        )


def _timestamp_text(value: datetime, field: str) -> str:
    try:
        return timestamp_text(value)
    except ValueError as exc:
        raise LiveDriftRegistryError(str(exc)) from exc


def _event_timestamp(event_type: str, payload: Mapping[str, object]) -> datetime:
    field = (
        "evaluated_at"
        if event_type == "drift_checkpoint_evaluated"
        else (
            "frozen_at"
            if event_type == "drift_envelope_frozen"
            else "observed_at"
            if event_type == "live_observation_recorded"
            else "occurred_at"
        )
    )
    value = payload.get(field)
    if not isinstance(value, str):
        raise LiveDriftRegistryError(f"{event_type} is missing canonical timestamp")
    try:
        parsed = parse_timestamp(value)
    except ValueError as exc:
        raise LiveDriftRegistryError(f"{event_type} has an invalid timestamp") from exc
    if timestamp_text(parsed) != value:
        raise LiveDriftRegistryError(f"{event_type} has a non-canonical timestamp")
    return parsed


def _events(state: Mapping[str, object]) -> list[dict[str, object]]:
    events = state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise LiveDriftRegistryError("live-drift events are malformed")
    return events


def _validate_hash_chain(events: Sequence[Mapping[str, object]]) -> None:
    previous_hash = _GENESIS_HASH
    event_ids: set[str] = set()
    for sequence, event in enumerate(events, start=1):
        content = {
            "sequence": event.get("sequence"),
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "payload": event.get("payload"),
            "previous_hash": event.get("previous_hash"),
        }
        expected = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        if (
            event.get("sequence") != sequence
            or event.get("previous_hash") != previous_hash
            or event.get("event_hash") != expected
            or not isinstance(event.get("event_id"), str)
            or not isinstance(event.get("event_type"), str)
            or not isinstance(event.get("payload"), dict)
        ):
            raise LiveDriftRegistryError("live-drift hash chain is invalid")
        event_id = str(event["event_id"])
        if event_id in event_ids:
            raise LiveDriftRegistryError("live-drift event identities are duplicated")
        event_ids.add(event_id)
        previous_hash = expected


def _verify_checkpoint(path: Path, content: bytes, events: Sequence[Mapping[str, object]]) -> None:
    if not events:
        if path.exists():
            raise LiveDriftRegistryError("empty live-drift history has an unexpected checkpoint")
        return
    try:
        checkpoint = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise LiveDriftRegistryError("live-drift head checkpoint is missing or invalid") from exc
    expected = {
        "schema_version": DRIFT_SCHEMA_VERSION,
        "event_count": len(events),
        "registry_checksum": hashlib.sha256(content).hexdigest(),
        "head_hash": events[-1].get("event_hash"),
    }
    if checkpoint != expected:
        raise LiveDriftRegistryError("live-drift head checkpoint does not match history")


def _envelope_from_payload(payload: Mapping[str, object]) -> PredictiveDriftEnvelope:
    try:
        metrics = tuple(
            DriftMetricExpectation.create(
                metric_id=str(item["metric_id"]),
                kind=DriftMetricKind(str(item["kind"])),
                direction=str(item["direction"]),
                watch_boundary=str(item["watch_boundary"]),
                pause_boundary=str(item["pause_boundary"]),
                minimum_observations=int(item["minimum_observations"]),
                window_sessions=int(item["window_sessions"]),
                unit=str(item["unit"]),
            )
            for item in payload["metrics"]
            if isinstance(item, Mapping)
        )
        envelope = PredictiveDriftEnvelope.create(
            strategy_id=str(payload["strategy_id"]),
            definition_fingerprint=str(payload["definition_fingerprint"]),
            source_identities=tuple(str(value) for value in payload["source_identities"]),
            metrics=metrics,
            activation_anchor=date.fromisoformat(str(payload["activation_anchor"])),
            checkpoint_interval_sessions=int(payload["checkpoint_interval_sessions"]),
            bootstrap_seed=int(payload["bootstrap_seed"]),
            bootstrap_repetitions=int(payload["bootstrap_repetitions"]),
            bootstrap_block_sessions=int(payload["bootstrap_block_sessions"]),
            frozen_at=parse_timestamp(str(payload["frozen_at"])),
            hard_guard_kinds=tuple(
                HardGuardKind(str(value)) for value in payload["hard_guard_kinds"]
            ),
        )
    except (DriftError, KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("drift envelope payload is malformed") from exc
    if envelope.envelope_id != payload.get("envelope_id"):
        raise LiveDriftRegistryError("drift envelope identity is invalid")
    if envelope.payload() != dict(payload):
        raise LiveDriftRegistryError("drift envelope payload is not canonical")
    return envelope


def _observation_from_payload(payload: Mapping[str, object]) -> DriftObservation:
    try:
        metrics = tuple(
            DriftMetricObservation.create(
                metric_id=str(item["metric_id"]),
                value=str(item["value"]),
                sample_count=int(item["sample_count"]),
            )
            for item in payload["metrics"]
            if isinstance(item, Mapping)
        )
        guards = tuple(
            HardGuardObservation.create(
                kind=HardGuardKind(str(item["kind"])),
                guard_id=str(item["guard_id"]),
                active=item["active"] is True,
                evidence_identity=str(item["evidence_identity"]),
                reason=str(item["reason"]),
            )
            for item in payload["hard_guards"]
            if isinstance(item, Mapping)
        )
        observation = DriftObservation.create(
            strategy_id=str(payload["strategy_id"]),
            envelope_id=str(payload["envelope_id"]),
            definition_fingerprint=str(payload["definition_fingerprint"]),
            session=date.fromisoformat(str(payload["session"])),
            observed_at=parse_timestamp(str(payload["observed_at"])),
            metrics=metrics,
            hard_guards=guards,
            source_identities=tuple(str(value) for value in payload["source_identities"]),
            completed_shadow_trades_total=int(payload["completed_shadow_trades_total"]),
        )
    except (DriftError, KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("live observation payload is malformed") from exc
    if observation.observation_id != payload.get("observation_id"):
        raise LiveDriftRegistryError("live observation identity is invalid")
    if observation.payload() != dict(payload):
        raise LiveDriftRegistryError("live observation payload is not canonical")
    return observation


def _metric_assessment_from_payload(payload: Mapping[str, object]) -> MetricAssessment:
    value = payload.get("value")
    try:
        return MetricAssessment(
            metric_id=str(payload["metric_id"]),
            assessment=DriftAssessment(str(payload["assessment"])),
            value=None if value is None else Decimal(str(value)),
            sample_count=int(payload["sample_count"]),
            reason=str(payload["reason"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("checkpoint metric assessment is malformed") from exc


def _guard_from_payload(payload: Mapping[str, object]) -> HardGuardObservation:
    try:
        return HardGuardObservation.create(
            kind=HardGuardKind(str(payload["kind"])),
            guard_id=str(payload["guard_id"]),
            active=payload["active"] is True,
            evidence_identity=str(payload["evidence_identity"]),
            reason=str(payload["reason"]),
        )
    except (DriftError, KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("checkpoint hard guard is malformed") from exc


def _checkpoint_from_payload(payload: Mapping[str, object]) -> DriftCheckpoint:
    try:
        checkpoint = DriftCheckpoint(
            checkpoint_id=str(payload["checkpoint_id"]),
            strategy_id=str(payload["strategy_id"]),
            envelope_id=str(payload["envelope_id"]),
            ordinal=int(payload["ordinal"]),
            session=date.fromisoformat(str(payload["session"])),
            assessment=DriftAssessment(str(payload["assessment"])),
            state=DriftState(str(payload["state"])),
            watch_streak=int(payload["watch_streak"]),
            metric_assessments=tuple(
                _metric_assessment_from_payload(item)
                for item in payload["metric_assessments"]
                if isinstance(item, Mapping)
            ),
            active_hard_guards=tuple(
                _guard_from_payload(item)
                for item in payload["active_hard_guards"]
                if isinstance(item, Mapping)
            ),
            completed_shadow_trades_total=int(payload["completed_shadow_trades_total"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("checkpoint payload is malformed") from exc
    expected_id = hashlib.sha256(
        canonical_json_bytes(
            {
                "strategy_id": checkpoint.strategy_id,
                "envelope_id": checkpoint.envelope_id,
                "ordinal": checkpoint.ordinal,
                "session": checkpoint.session.isoformat(),
                "assessment": checkpoint.assessment.value,
                "state": checkpoint.state.value,
                "watch_streak": checkpoint.watch_streak,
                "metric_assessments": [item.payload() for item in checkpoint.metric_assessments],
                "active_hard_guards": [item.payload() for item in checkpoint.active_hard_guards],
            }
        )
    ).hexdigest()
    if checkpoint.checkpoint_id != expected_id:
        raise LiveDriftRegistryError("checkpoint identity is invalid")
    return checkpoint


def _validate_clean_payload(payload: Mapping[str, object]) -> None:
    try:
        session_text = payload["session"]
        if (
            not isinstance(session_text, str)
            or date.fromisoformat(session_text).isoformat() != session_text
        ):
            raise ValueError("session is not canonical")
        _required_text(payload["evidence_identity"], "evidence_identity")
        occurred_text = payload["occurred_at"]
        if not isinstance(occurred_text, str):
            raise ValueError("timestamp is not text")
        occurred_at = parse_timestamp(occurred_text)
        if timestamp_text(occurred_at) != occurred_text:
            raise ValueError("timestamp is not canonical")
    except (KeyError, TypeError, ValueError) as exc:
        raise LiveDriftRegistryError("clean check payload is malformed") from exc

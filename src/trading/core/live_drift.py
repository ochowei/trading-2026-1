"""Frozen live-drift expectations, observations, checkpoints, and recovery gates.

This module deliberately contains no broker integration.  It models the evidence boundary used
by dry-run followup: paper observations come from the frozen strategy definition, execution
observations come from confirmed ledger fills, and portfolio observations come from verified
ledger positions marked with validated market data.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from trading.core.accounting import canonical_json_bytes, decimal_text, timestamp_text, to_decimal

DRIFT_SCHEMA_VERSION = 1
DRIFT_ENGINE_VERSION = "live-drift-v1"
NORMAL_RECOVERY_SESSIONS = 126
NORMAL_RECOVERY_SHADOW_TRADES = 6
RECOVERY_CHECKPOINTS = 2


class DriftError(ValueError):
    """A drift contract, observation, or recovery decision is unsafe."""


class DriftState(StrEnum):
    """The Phase 8 health overlay for one Phase 7 Active strategy."""

    HEALTHY = "healthy"
    WATCH = "watch"
    PAUSED = "paused"


class DriftAssessment(StrEnum):
    """One scheduled checkpoint's evidence classification."""

    NORMAL = "normal"
    WATCH = "watch"
    PAUSED = "paused"
    INCONCLUSIVE = "inconclusive"


class DriftDirection(StrEnum):
    """Which tail of a metric is adverse."""

    LOWER_IS_WORSE = "lower_is_worse"
    HIGHER_IS_WORSE = "higher_is_worse"


class DriftMetricKind(StrEnum):
    """Phase 8 monitor families."""

    PERFORMANCE = "performance"
    SIGNAL = "signal"
    EXECUTION = "execution"
    PORTFOLIO = "portfolio"
    UTILIZATION = "utilization"
    CONCENTRATION = "concentration"


class HardGuardKind(StrEnum):
    """Immediate no-new-entry guard families."""

    DATA = "data"
    LEDGER = "ledger"
    RECONCILIATION = "reconciliation"
    EXECUTION = "execution"
    STRESS_RISK = "stress_risk"


_INTEGRITY_ONLY_GUARDS = frozenset(
    {HardGuardKind.DATA, HardGuardKind.LEDGER, HardGuardKind.RECONCILIATION}
)


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DriftError(f"{field} must be a non-empty string")
    return value.strip()


def _digest(value: str, field: str) -> str:
    normalized = _required_text(value, field)
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise DriftError(f"{field} must be a lowercase SHA-256 digest")
    return normalized


def _decimal(value: Decimal | int | str, field: str) -> Decimal:
    try:
        return to_decimal(value, field)
    except TypeError:
        raise
    except ValueError as exc:
        raise DriftError(str(exc)) from exc


def _date(value: date, field: str) -> date:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise DriftError(f"{field} must be a date")
    return value


def _timestamp(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DriftError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


def _unique_sorted(values: Sequence[str], field: str) -> tuple[str, ...]:
    normalized = tuple(sorted(_required_text(value, field) for value in values))
    if len(set(normalized)) != len(normalized):
        raise DriftError(f"{field} must be unique")
    return normalized


@dataclass(frozen=True, slots=True)
class DriftMetricExpectation:
    """One immutable metric boundary inside a predictive drift envelope."""

    metric_id: str
    kind: DriftMetricKind
    direction: DriftDirection
    watch_boundary: Decimal
    pause_boundary: Decimal
    minimum_observations: int
    window_sessions: int
    unit: str = "ratio"

    @classmethod
    def create(
        cls,
        *,
        metric_id: str,
        direction: DriftDirection,
        watch_boundary: Decimal | int | str,
        pause_boundary: Decimal | int | str,
        minimum_observations: int,
        window_sessions: int,
        kind: DriftMetricKind = DriftMetricKind.PERFORMANCE,
        unit: str = "ratio",
    ) -> DriftMetricExpectation:
        return cls(
            metric_id=_required_text(metric_id, "metric_id"),
            kind=DriftMetricKind(kind),
            direction=DriftDirection(direction),
            watch_boundary=_decimal(watch_boundary, "watch_boundary"),
            pause_boundary=_decimal(pause_boundary, "pause_boundary"),
            minimum_observations=minimum_observations,
            window_sessions=window_sessions,
            unit=_required_text(unit, "unit"),
        )

    def __post_init__(self) -> None:
        if isinstance(self.minimum_observations, bool) or not isinstance(
            self.minimum_observations, int
        ):
            raise DriftError("minimum_observations must be an integer")
        if isinstance(self.window_sessions, bool) or not isinstance(self.window_sessions, int):
            raise DriftError("window_sessions must be an integer")
        if self.minimum_observations <= 0:
            raise DriftError("minimum_observations must be positive")
        if self.window_sessions <= 0:
            raise DriftError("window_sessions must be positive")
        if self.direction is DriftDirection.LOWER_IS_WORSE:
            if self.pause_boundary > self.watch_boundary:
                raise DriftError("lower-is-worse pause boundary must not exceed watch boundary")
        elif self.pause_boundary < self.watch_boundary:
            raise DriftError("higher-is-worse pause boundary must not be below watch boundary")
        if not self.watch_boundary.is_finite() or not self.pause_boundary.is_finite():
            raise DriftError("metric boundaries must be finite")

    def payload(self) -> dict[str, object]:
        return {
            "metric_id": self.metric_id,
            "kind": self.kind.value,
            "direction": self.direction.value,
            "watch_boundary": decimal_text(self.watch_boundary),
            "pause_boundary": decimal_text(self.pause_boundary),
            "minimum_observations": self.minimum_observations,
            "window_sessions": self.window_sessions,
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class PredictiveDriftEnvelope:
    """The frozen pre-activation expectation used by every later checkpoint."""

    envelope_id: str
    strategy_id: str
    definition_fingerprint: str
    source_identities: tuple[str, ...]
    metrics: tuple[DriftMetricExpectation, ...]
    activation_anchor: date
    checkpoint_interval_sessions: int
    bootstrap_seed: int
    bootstrap_repetitions: int
    bootstrap_block_sessions: int
    frozen_at: datetime
    hard_guard_kinds: tuple[HardGuardKind, ...]
    engine_version: str = DRIFT_ENGINE_VERSION

    @classmethod
    def create(
        cls,
        *,
        strategy_id: str,
        definition_fingerprint: str,
        source_identities: Sequence[str],
        metrics: Sequence[DriftMetricExpectation],
        activation_anchor: date,
        checkpoint_interval_sessions: int,
        bootstrap_seed: int,
        bootstrap_repetitions: int,
        bootstrap_block_sessions: int,
        frozen_at: datetime,
        hard_guard_kinds: Sequence[HardGuardKind] = tuple(HardGuardKind),
    ) -> PredictiveDriftEnvelope:
        normalized_metrics = tuple(sorted(metrics, key=lambda item: item.metric_id))
        if not normalized_metrics:
            raise DriftError("predictive envelope requires at least one metric")
        metric_ids = tuple(item.metric_id for item in normalized_metrics)
        if len(set(metric_ids)) != len(metric_ids):
            raise DriftError("predictive envelope metric identities must be unique")
        candidate = cls(
            envelope_id="",
            strategy_id=_required_text(strategy_id, "strategy_id"),
            definition_fingerprint=_digest(definition_fingerprint, "definition_fingerprint"),
            source_identities=_unique_sorted(source_identities, "source_identity"),
            metrics=normalized_metrics,
            activation_anchor=_date(activation_anchor, "activation_anchor"),
            checkpoint_interval_sessions=checkpoint_interval_sessions,
            bootstrap_seed=bootstrap_seed,
            bootstrap_repetitions=bootstrap_repetitions,
            bootstrap_block_sessions=bootstrap_block_sessions,
            frozen_at=_timestamp(frozen_at, "frozen_at"),
            hard_guard_kinds=tuple(
                sorted(
                    set(HardGuardKind(item) for item in hard_guard_kinds),
                    key=lambda item: item.value,
                )
            ),
        )
        identity = hashlib.sha256(canonical_json_bytes(candidate._identity_payload())).hexdigest()
        return replace(candidate, envelope_id=identity)

    def __post_init__(self) -> None:
        if self.envelope_id and (
            len(self.envelope_id) != 64
            or any(character not in "0123456789abcdef" for character in self.envelope_id)
        ):
            raise DriftError("envelope_id must be a lowercase SHA-256 digest")
        if isinstance(self.checkpoint_interval_sessions, bool) or not isinstance(
            self.checkpoint_interval_sessions, int
        ):
            raise DriftError("checkpoint_interval_sessions must be an integer")
        if self.checkpoint_interval_sessions <= 0:
            raise DriftError("checkpoint_interval_sessions must be positive")
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (
                self.bootstrap_seed,
                self.bootstrap_repetitions,
                self.bootstrap_block_sessions,
            )
        ):
            raise DriftError("bootstrap policy values must be integers")
        if self.bootstrap_repetitions <= 0 or self.bootstrap_block_sessions <= 0:
            raise DriftError("bootstrap policy values must be positive")
        if not self.source_identities:
            raise DriftError("predictive envelope requires source identities")
        if not self.hard_guard_kinds:
            raise DriftError("predictive envelope requires hard-guard kinds")
        from trading.market_data import PrimaryUSSessionCalendar

        try:
            if (
                PrimaryUSSessionCalendar().session_on_or_before(self.activation_anchor)
                != self.activation_anchor
            ):
                raise DriftError("activation_anchor must be a completed XNYS session")
        except (TypeError, ValueError) as exc:
            raise DriftError("activation_anchor must be a completed XNYS session") from exc

    def _identity_payload(self) -> dict[str, object]:
        return {
            "schema_version": DRIFT_SCHEMA_VERSION,
            "engine_version": self.engine_version,
            "strategy_id": self.strategy_id,
            "definition_fingerprint": self.definition_fingerprint,
            "source_identities": list(self.source_identities),
            "metrics": [metric.payload() for metric in self.metrics],
            "activation_anchor": self.activation_anchor.isoformat(),
            "checkpoint_interval_sessions": self.checkpoint_interval_sessions,
            "bootstrap_seed": self.bootstrap_seed,
            "bootstrap_repetitions": self.bootstrap_repetitions,
            "bootstrap_block_sessions": self.bootstrap_block_sessions,
            "frozen_at": timestamp_text(self.frozen_at),
            "hard_guard_kinds": [kind.value for kind in self.hard_guard_kinds],
        }

    def payload(self) -> dict[str, object]:
        return {"envelope_id": self.envelope_id, **self._identity_payload()}

    def metric(self, metric_id: str) -> DriftMetricExpectation:
        try:
            return next(metric for metric in self.metrics if metric.metric_id == metric_id)
        except StopIteration as exc:
            raise DriftError(f"metric is not frozen in envelope: {metric_id}") from exc

    def expected_checkpoint(self, ordinal: int) -> date:
        if ordinal <= 0:
            raise DriftError("checkpoint ordinal must be positive")
        # Checkpoints are measured in completed market sessions, not calendar days.  Keeping
        # this lookup at the domain boundary prevents a weekend or exchange holiday from being
        # treated as a completed observation and makes the schedule deterministic for replay.
        from trading.market_data import PrimaryUSSessionCalendar

        try:
            return PrimaryUSSessionCalendar().session_offset(
                self.activation_anchor,
                self.checkpoint_interval_sessions * ordinal,
            )
        except (TypeError, ValueError) as exc:
            raise DriftError("checkpoint schedule is not a valid XNYS session schedule") from exc


@dataclass(frozen=True, slots=True)
class DriftMetricObservation:
    """One metric value and its independent sample count at a completed session."""

    metric_id: str
    value: Decimal
    sample_count: int

    @classmethod
    def create(
        cls,
        *,
        metric_id: str,
        value: Decimal | int | str,
        sample_count: int,
    ) -> DriftMetricObservation:
        return cls(
            metric_id=_required_text(metric_id, "metric_id"),
            value=_decimal(value, "metric_value"),
            sample_count=sample_count,
        )

    def __post_init__(self) -> None:
        if isinstance(self.sample_count, bool) or not isinstance(self.sample_count, int):
            raise DriftError("metric sample_count must be an integer")
        if self.sample_count < 0:
            raise DriftError("metric sample_count cannot be negative")

    def payload(self) -> dict[str, object]:
        return {
            "metric_id": self.metric_id,
            "value": decimal_text(self.value),
            "sample_count": self.sample_count,
        }


@dataclass(frozen=True, slots=True)
class HardGuardObservation:
    """One source-specific hard guard observation."""

    kind: HardGuardKind
    guard_id: str
    active: bool
    evidence_identity: str
    reason: str

    @classmethod
    def create(
        cls,
        *,
        kind: HardGuardKind,
        guard_id: str,
        active: bool,
        evidence_identity: str,
        reason: str,
    ) -> HardGuardObservation:
        return cls(
            kind=HardGuardKind(kind),
            guard_id=_required_text(guard_id, "guard_id"),
            active=active,
            evidence_identity=_required_text(evidence_identity, "evidence_identity"),
            reason=_required_text(reason, "reason"),
        )

    def __post_init__(self) -> None:
        if not isinstance(self.active, bool):
            raise DriftError("hard guard active must be a boolean")

    def payload(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "guard_id": self.guard_id,
            "active": self.active,
            "evidence_identity": self.evidence_identity,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class DriftObservation:
    """A complete, immutable monitor observation for one completed session."""

    observation_id: str
    strategy_id: str
    envelope_id: str
    definition_fingerprint: str
    session: date
    observed_at: datetime
    metrics: tuple[DriftMetricObservation, ...]
    hard_guards: tuple[HardGuardObservation, ...]
    source_identities: tuple[str, ...]
    completed_shadow_trades_total: int

    @classmethod
    def create(
        cls,
        *,
        strategy_id: str,
        envelope_id: str,
        definition_fingerprint: str,
        session: date,
        observed_at: datetime,
        metrics: Sequence[DriftMetricObservation],
        hard_guards: Sequence[HardGuardObservation] = (),
        source_identities: Sequence[str] = (),
        completed_shadow_trades_total: int = 0,
    ) -> DriftObservation:
        normalized_metrics = tuple(sorted(metrics, key=lambda item: item.metric_id))
        metric_ids = tuple(item.metric_id for item in normalized_metrics)
        if len(set(metric_ids)) != len(metric_ids):
            raise DriftError("observation metric identities must be unique")
        normalized_guards = tuple(
            sorted(hard_guards, key=lambda item: (item.kind.value, item.guard_id))
        )
        guard_ids = tuple((item.kind, item.guard_id) for item in normalized_guards)
        if len(set(guard_ids)) != len(guard_ids):
            raise DriftError("observation hard-guard identities must be unique")
        candidate = cls(
            observation_id="",
            strategy_id=_required_text(strategy_id, "strategy_id"),
            envelope_id=_digest(envelope_id, "envelope_id"),
            definition_fingerprint=_digest(definition_fingerprint, "definition_fingerprint"),
            session=_date(session, "session"),
            observed_at=_timestamp(observed_at, "observed_at"),
            metrics=normalized_metrics,
            hard_guards=normalized_guards,
            source_identities=_unique_sorted(source_identities, "source_identity"),
            completed_shadow_trades_total=completed_shadow_trades_total,
        )
        if isinstance(candidate.completed_shadow_trades_total, bool) or not isinstance(
            candidate.completed_shadow_trades_total, int
        ):
            raise DriftError("completed_shadow_trades_total must be an integer")
        if candidate.completed_shadow_trades_total < 0:
            raise DriftError("completed_shadow_trades_total cannot be negative")
        identity = hashlib.sha256(canonical_json_bytes(candidate._identity_payload())).hexdigest()
        return replace(candidate, observation_id=identity)

    def _identity_payload(self) -> dict[str, object]:
        return {
            "strategy_id": self.strategy_id,
            "envelope_id": self.envelope_id,
            "definition_fingerprint": self.definition_fingerprint,
            "session": self.session.isoformat(),
            "observed_at": timestamp_text(self.observed_at),
            "metrics": [metric.payload() for metric in self.metrics],
            "hard_guards": [guard.payload() for guard in self.hard_guards],
            "source_identities": list(self.source_identities),
            "completed_shadow_trades_total": self.completed_shadow_trades_total,
        }

    def payload(self) -> dict[str, object]:
        return {"observation_id": self.observation_id, **self._identity_payload()}


@dataclass(frozen=True, slots=True)
class MetricAssessment:
    """A checkpoint classification for one frozen metric."""

    metric_id: str
    assessment: DriftAssessment
    value: Decimal | None
    sample_count: int
    reason: str

    def payload(self) -> dict[str, object]:
        return {
            "metric_id": self.metric_id,
            "assessment": self.assessment.value,
            "value": decimal_text(self.value) if self.value is not None else None,
            "sample_count": self.sample_count,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class DriftCheckpoint:
    """A deterministic scheduled checkpoint projection."""

    checkpoint_id: str
    strategy_id: str
    envelope_id: str
    ordinal: int
    session: date
    assessment: DriftAssessment
    state: DriftState
    watch_streak: int
    metric_assessments: tuple[MetricAssessment, ...]
    active_hard_guards: tuple[HardGuardObservation, ...]
    completed_shadow_trades_total: int

    def payload(self) -> dict[str, object]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "strategy_id": self.strategy_id,
            "envelope_id": self.envelope_id,
            "ordinal": self.ordinal,
            "session": self.session.isoformat(),
            "assessment": self.assessment.value,
            "state": self.state.value,
            "watch_streak": self.watch_streak,
            "metric_assessments": [item.payload() for item in self.metric_assessments],
            "active_hard_guards": [item.payload() for item in self.active_hard_guards],
            "completed_shadow_trades_total": self.completed_shadow_trades_total,
        }


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """The recomputed result of a recovery gate; callers cannot set state directly."""

    eligible: bool
    recovery_kind: str
    reasons: tuple[str, ...]
    sessions_after_pause: int
    completed_shadow_trades_after_pause: int
    normal_checkpoints: int
    clean_checks: int


def _classify_metric(
    expectation: DriftMetricExpectation,
    observation: DriftMetricObservation | None,
) -> MetricAssessment:
    if observation is None:
        return MetricAssessment(
            metric_id=expectation.metric_id,
            assessment=DriftAssessment.INCONCLUSIVE,
            value=None,
            sample_count=0,
            reason="no observation covers this checkpoint",
        )
    if observation.sample_count < expectation.minimum_observations:
        return MetricAssessment(
            metric_id=expectation.metric_id,
            assessment=DriftAssessment.INCONCLUSIVE,
            value=observation.value,
            sample_count=observation.sample_count,
            reason="metric sample count is below the frozen minimum",
        )
    if expectation.direction is DriftDirection.LOWER_IS_WORSE:
        if observation.value <= expectation.pause_boundary:
            assessment = DriftAssessment.PAUSED
        elif observation.value <= expectation.watch_boundary:
            assessment = DriftAssessment.WATCH
        else:
            assessment = DriftAssessment.NORMAL
    elif observation.value >= expectation.pause_boundary:
        assessment = DriftAssessment.PAUSED
    elif observation.value >= expectation.watch_boundary:
        assessment = DriftAssessment.WATCH
    else:
        assessment = DriftAssessment.NORMAL
    return MetricAssessment(
        metric_id=expectation.metric_id,
        assessment=assessment,
        value=observation.value,
        sample_count=observation.sample_count,
        reason=f"{expectation.direction.value} envelope classification",
    )


def evaluate_checkpoint(
    envelope: PredictiveDriftEnvelope,
    *,
    ordinal: int,
    session: date,
    observations: Sequence[DriftObservation],
    prior_state: DriftState = DriftState.HEALTHY,
    prior_watch_streak: int = 0,
) -> DriftCheckpoint:
    """Evaluate one fixed checkpoint from verified observations."""
    checkpoint_session = _date(session, "checkpoint session")
    if ordinal <= 0:
        raise DriftError("checkpoint ordinal must be positive")
    expected = envelope.expected_checkpoint(ordinal)
    if checkpoint_session != expected:
        raise DriftError("checkpoint session does not match frozen schedule")
    relevant = [
        observation
        for observation in observations
        if observation.envelope_id == envelope.envelope_id
        and observation.strategy_id == envelope.strategy_id
        and observation.definition_fingerprint == envelope.definition_fingerprint
        and observation.session <= checkpoint_session
    ]
    from trading.market_data import PrimaryUSSessionCalendar

    calendar = PrimaryUSSessionCalendar()
    metric_assessments: list[MetricAssessment] = []
    for expectation in envelope.metrics:
        window_start = calendar.session_offset(
            checkpoint_session,
            -(expectation.window_sessions - 1),
        )
        latest_metric: DriftMetricObservation | None = None
        for observation in sorted(relevant, key=lambda item: (item.session, item.observed_at)):
            if observation.session < window_start:
                continue
            for metric in observation.metrics:
                if metric.metric_id == expectation.metric_id:
                    latest_metric = metric
        metric_assessments.append(_classify_metric(expectation, latest_metric))
    metric_assessment_values = tuple(metric_assessments)
    active_guards: dict[tuple[HardGuardKind, str], HardGuardObservation] = {}
    for observation in sorted(relevant, key=lambda item: (item.session, item.observed_at)):
        for guard in observation.hard_guards:
            active_guards[(guard.kind, guard.guard_id)] = guard
    active = tuple(
        sorted(
            (guard for guard in active_guards.values() if guard.active),
            key=lambda item: (item.kind.value, item.guard_id),
        )
    )
    has_pause = bool(active) or any(
        item.assessment is DriftAssessment.PAUSED for item in metric_assessment_values
    )
    has_watch = any(item.assessment is DriftAssessment.WATCH for item in metric_assessment_values)
    inconclusive = any(
        item.assessment is DriftAssessment.INCONCLUSIVE for item in metric_assessment_values
    )
    if has_pause:
        state = DriftState.PAUSED
        assessment = DriftAssessment.PAUSED
        watch_streak = prior_watch_streak
    elif has_watch or inconclusive:
        watch_streak = prior_watch_streak + 1 if prior_state is DriftState.WATCH else 1
        if watch_streak >= 2:
            state = DriftState.PAUSED
            assessment = DriftAssessment.PAUSED
        else:
            state = DriftState.WATCH
            assessment = DriftAssessment.WATCH if has_watch else DriftAssessment.INCONCLUSIVE
    else:
        state = DriftState.HEALTHY
        assessment = DriftAssessment.NORMAL
        watch_streak = 0
    payload = {
        "strategy_id": envelope.strategy_id,
        "envelope_id": envelope.envelope_id,
        "ordinal": ordinal,
        "session": checkpoint_session.isoformat(),
        "assessment": assessment.value,
        "state": state.value,
        "watch_streak": watch_streak,
        "metric_assessments": [item.payload() for item in metric_assessment_values],
        "active_hard_guards": [item.payload() for item in active],
    }
    checkpoint_id = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    total_trades = max(
        (observation.completed_shadow_trades_total for observation in relevant),
        default=0,
    )
    return DriftCheckpoint(
        checkpoint_id=checkpoint_id,
        strategy_id=envelope.strategy_id,
        envelope_id=envelope.envelope_id,
        ordinal=ordinal,
        session=checkpoint_session,
        assessment=assessment,
        state=state,
        watch_streak=watch_streak,
        metric_assessments=metric_assessment_values,
        active_hard_guards=active,
        completed_shadow_trades_total=total_trades,
    )


def evaluate_recovery(
    envelope: PredictiveDriftEnvelope,
    *,
    pause_checkpoint: DriftCheckpoint | None = None,
    pause_session: date | None = None,
    pause_completed_shadow_trades_total: int = 0,
    observations: Sequence[DriftObservation],
    checkpoints: Sequence[DriftCheckpoint],
    current_session: date,
    hard_guards_clear: bool,
    cause_kinds: Sequence[HardGuardKind] = (),
    clean_check_sessions: Sequence[date] = (),
) -> RecoveryDecision:
    """Recompute general or integrity-only recovery eligibility."""
    if pause_checkpoint is not None:
        if pause_checkpoint.state is not DriftState.PAUSED:
            raise DriftError("recovery requires a paused checkpoint")
        if pause_checkpoint.envelope_id != envelope.envelope_id:
            raise DriftError("pause checkpoint does not match envelope")
        reference_session = pause_checkpoint.session
        reference_total = pause_checkpoint.completed_shadow_trades_total
    elif pause_session is not None:
        reference_session = _date(pause_session, "pause session")
        reference_total = pause_completed_shadow_trades_total
    else:
        raise DriftError("recovery requires a paused checkpoint or hard-guard pause session")
    current = _date(current_session, "current session")
    if current <= reference_session:
        raise DriftError("recovery current session must follow the pause")
    from trading.market_data import PrimaryUSSessionCalendar

    calendar = PrimaryUSSessionCalendar()
    if calendar.session_on_or_before(current) != current:
        raise DriftError("recovery current session must be an XNYS session")
    later_observations = [
        observation
        for observation in observations
        if observation.envelope_id == envelope.envelope_id
        and observation.strategy_id == envelope.strategy_id
        and reference_session < observation.session <= current
    ]
    sessions = len({observation.session for observation in later_observations})
    if any(
        calendar.session_on_or_before(observation.session) != observation.session
        for observation in later_observations
    ):
        raise DriftError("recovery observations must use XNYS sessions")
    before_total = max(
        (
            observation.completed_shadow_trades_total
            for observation in observations
            if observation.envelope_id == envelope.envelope_id
            and observation.session <= reference_session
        ),
        default=reference_total,
    )
    after_total = max(
        (observation.completed_shadow_trades_total for observation in later_observations),
        default=before_total,
    )
    trades = max(0, after_total - before_total)
    later_checkpoints = sorted(
        (
            checkpoint
            for checkpoint in checkpoints
            if checkpoint.envelope_id == envelope.envelope_id
            and reference_session < checkpoint.session <= current
        ),
        key=lambda checkpoint: checkpoint.ordinal,
    )
    normal = [
        checkpoint
        for checkpoint in later_checkpoints
        if checkpoint.state is DriftState.HEALTHY
        and checkpoint.assessment is DriftAssessment.NORMAL
        and not checkpoint.active_hard_guards
    ]
    recent_normal = normal[-RECOVERY_CHECKPOINTS:]
    normal_ok = len(recent_normal) == RECOVERY_CHECKPOINTS and all(
        recent_normal[index].ordinal + 1 == recent_normal[index + 1].ordinal
        for index in range(len(recent_normal) - 1)
    )
    guard_set = tuple(HardGuardKind(kind) for kind in cause_kinds)
    integrity_only = bool(guard_set) and all(kind in _INTEGRITY_ONLY_GUARDS for kind in guard_set)
    clean_sessions = tuple(
        sorted(set(_date(item, "clean check session") for item in clean_check_sessions))
    )
    if any(
        session <= reference_session
        or session > current
        or calendar.session_on_or_before(session) != session
        for session in clean_sessions
    ):
        raise DriftError("clean checks must be completed XNYS sessions after the pause")
    if integrity_only:
        clean_ok = len(clean_sessions) >= 2
        eligible = hard_guards_clear and clean_ok
        reasons: list[str] = []
        if not hard_guards_clear:
            reasons.append("hard guards remain active")
        if not clean_ok:
            reasons.append("two distinct clean checks are required")
        return RecoveryDecision(
            eligible=eligible,
            recovery_kind="data_ledger_only",
            reasons=tuple(reasons),
            sessions_after_pause=sessions,
            completed_shadow_trades_after_pause=trades,
            normal_checkpoints=len(normal),
            clean_checks=len(clean_sessions),
        )
    reasons = []
    if not hard_guards_clear:
        reasons.append("hard guards remain active")
    if sessions < NORMAL_RECOVERY_SESSIONS:
        reasons.append(f"at least {NORMAL_RECOVERY_SESSIONS} later sessions are required")
    if trades < NORMAL_RECOVERY_SHADOW_TRADES:
        reasons.append(
            f"at least {NORMAL_RECOVERY_SHADOW_TRADES} completed Shadow trades are required"
        )
    if not normal_ok:
        reasons.append("two consecutive scheduled checkpoints must be normal")
    return RecoveryDecision(
        eligible=not reasons,
        recovery_kind="general",
        reasons=tuple(reasons),
        sessions_after_pause=sessions,
        completed_shadow_trades_after_pause=trades,
        normal_checkpoints=len(normal),
        clean_checks=len(clean_sessions),
    )


def is_integrity_only_guard(kind: HardGuardKind) -> bool:
    """Return whether a guard may use the expedited recovery gate."""
    return HardGuardKind(kind) in _INTEGRITY_ONLY_GUARDS

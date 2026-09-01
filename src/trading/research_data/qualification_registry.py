"""Append-only persistence for Historical and Shadow qualification lifecycle events."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from trading.core.accounting import (
    canonical_json_bytes,
    decimal_text,
    parse_timestamp,
    timestamp_text,
)
from trading.core.ledger_storage import atomic_write, locked_file
from trading.core.qualification import (
    EVIDENCE_ROLES,
    HISTORICAL_QUALIFICATION_GATE_NAMES,
    QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY,
    RETROSPECTIVE_EVIDENCE_ROLES,
    SHADOW_ACTIVATION_GATE_NAMES,
    EvaluationEvidenceAudit,
    EvaluationFold,
    ExposureMatchedRandomSample,
    ForwardSelectionEpoch,
    HistoricalAggregateEvidence,
    HistoricalBenchmarkEvidence,
    HistoricalBenchmarkPolicy,
    HistoricalFoldEvidence,
    HistoricalQualificationPlan,
    HistoricalScreenResult,
    HistoricalScreenThresholds,
    QualificationGate,
    QualificationRoleCalendar,
    RetrospectiveSelectionCheckpoint,
    SelectionAdjustmentPolicy,
    SelectionAdjustmentResult,
    ShadowActivationEvaluation,
    ShadowEvidence,
    ShadowRegistration,
    StudyQualificationIdentity,
    validate_historical_screen_result,
    validate_historical_thresholds,
    validate_study_qualification_identity,
)
from trading.core.sleeve_engine import ExecutionCostPolicy
from trading.research_data.definitions import ResearchDefinitionStore
from trading.research_data.models import DefinitionBlobRef

QUALIFICATION_REGISTRY_SCHEMA_VERSION = 1
_GENESIS_HASH = "0" * 64


class QualificationRegistryError(RuntimeError):
    """Qualification history is malformed, conflicting, or violates lifecycle order."""


class QualificationRegistry:
    """A private append-only event history for prospective qualification state."""

    def __init__(
        self,
        path: Path,
        *,
        lock_timeout_seconds: float = 10.0,
        definition_store: ResearchDefinitionStore | None = None,
        definition_verifier: Callable[[str, int, str], None] | None = None,
        current_definition_resolver: Callable[[str, str], str] | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(f".{self.path.name}.lock")
        self.checkpoint_path = self.path.with_name(f".{self.path.name}.head.json")
        self.lock_timeout_seconds = lock_timeout_seconds
        self.now = now or (lambda: datetime.now(UTC))
        store = definition_store or ResearchDefinitionStore(Path(".research-data/blobs"))
        self.definition_verifier = definition_verifier or (
            lambda digest, byte_count, fingerprint: store.load(
                DefinitionBlobRef(
                    digest=digest,
                    byte_count=byte_count,
                    fingerprint=fingerprint,
                )
            )
        )
        self.current_definition_resolver = (
            current_definition_resolver or _missing_current_definition
        )

    def read(self) -> dict[str, object]:
        return copy.deepcopy(self._load_unlocked())

    def initialize(self) -> dict[str, object]:
        """Materialize an empty verified registry/checkpoint without adding an event."""
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            if not self.path.exists():
                content = canonical_json_bytes(state)
                atomic_write(self.path, content, replace=False)
                _write_head_checkpoint(self.checkpoint_path, content, [])
            return copy.deepcopy(state)

    def result_sections(
        self,
        *,
        historical_plan_id: str,
        shadow_id: str | None = None,
    ) -> dict[str, object]:
        """Project verified lifecycle events into result-schema evidence sections."""
        state = self._load_unlocked()
        plan = copy.deepcopy(
            dict(
                _payload(
                    _event_for_identity(
                        state,
                        event_type="historical_plan",
                        identity_name="plan_id",
                        identity=historical_plan_id,
                    )
                )
            )
        )
        screen = copy.deepcopy(
            dict(
                _payload(
                    _event_for_identity(
                        state,
                        event_type="historical_screen",
                        identity_name="plan_id",
                        identity=historical_plan_id,
                    )
                )
            )
        )
        folds = screen.pop("folds", None)
        if not isinstance(folds, list):
            raise QualificationRegistryError("historical screen fold evidence is malformed")
        shadow: dict[str, object] = {}
        if shadow_id is not None:
            registration = copy.deepcopy(dict(_payload(_registration_event(state, shadow_id))))
            if registration.get("historical_plan_id") != historical_plan_id:
                raise QualificationRegistryError(
                    "Shadow registration belongs to a different historical plan"
                )
            evidence_events = [
                event
                for event in _events(state)
                if event.get("event_type") == "shadow_evidence"
                and isinstance(event.get("payload"), Mapping)
                and event["payload"].get("shadow_id") == shadow_id
            ]
            activation_events = [
                event
                for event in _events(state)
                if event.get("event_type") == "activation_evaluation"
                and isinstance(event.get("payload"), Mapping)
                and event["payload"].get("shadow_id") == shadow_id
            ]
            latest_evidence = evidence_events[-1] if evidence_events else None
            latest_as_of = (
                _payload(latest_evidence).get("as_of") if latest_evidence is not None else None
            )
            matching_activation = next(
                (
                    event
                    for event in reversed(activation_events)
                    if _payload(event).get("evaluated_at") == latest_as_of
                ),
                None,
            )
            shadow = {
                "registration": registration,
                "evidence": (
                    copy.deepcopy(dict(_payload(latest_evidence)))
                    if latest_evidence is not None
                    else {}
                ),
                "activation": (
                    copy.deepcopy(dict(_payload(matching_activation)))
                    if matching_activation is not None
                    else {}
                ),
            }
        return {
            "development_summary": {
                "historical_plan": plan,
                "historical_screen": screen,
            },
            "historical_stability_folds": folds,
            "shadow_evidence": shadow,
        }

    def historical_plan(self, plan_id: str) -> HistoricalQualificationPlan:
        """Return one verified frozen plan as a typed domain value."""
        state = self._load_unlocked()
        event = _event_for_identity(
            state,
            event_type="historical_plan",
            identity_name="plan_id",
            identity=plan_id,
        )
        return _historical_plan_from_payload(_payload(event))

    def historical_screen(self, plan_id: str) -> HistoricalScreenResult:
        """Return one fully rehydrated and recomputed historical screen."""
        state = self._load_unlocked()
        event = _event_for_identity(
            state,
            event_type="historical_screen",
            identity_name="plan_id",
            identity=plan_id,
        )
        payload = _payload(event)
        plan = _historical_plan_from_payload(
            _payload(
                _event_for_identity(
                    state,
                    event_type="historical_plan",
                    identity_name="plan_id",
                    identity=plan_id,
                )
            )
        )
        screen = _historical_screen_from_payload(payload)
        try:
            evaluated_at = parse_timestamp(str(payload["evaluated_at"]))
            if evaluated_at.date() <= plan.folds[-1].outcome_end:
                raise ValueError("historical screen predates complete fold outcomes")
            validate_historical_screen_result(plan, screen)
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise QualificationRegistryError(
                f"historical screen payload is malformed: {exc}"
            ) from exc
        return screen

    def register_historical_plan(self, plan: HistoricalQualificationPlan) -> str:
        """Persist frozen folds and thresholds before recording their outcomes."""
        self.validate_historical_plan_registration(plan)
        payload = _historical_plan_payload(plan)
        event_id = f"historical-plan:{plan.plan_id}"
        selection_boundary = plan.forward_selection_epoch or plan.retrospective_selection_checkpoint
        if selection_boundary is None:
            self._append(
                event_id=event_id,
                event_type="historical_plan",
                payload=payload,
            )
        else:
            with locked_file(self.lock_path, self.lock_timeout_seconds):
                state = self._load_unlocked()
                self._validate_plan_state_for_registration(state, plan, event_id)
                self._append_unlocked(
                    state,
                    event_id=event_id,
                    event_type="historical_plan",
                    payload=payload,
                )
        return plan.plan_id

    def validate_historical_plan_registration(self, plan: HistoricalQualificationPlan) -> None:
        """Check a complete plan and current registry state without appending an event."""
        try:
            validate_historical_thresholds(plan.thresholds)
        except ValueError as exc:
            raise QualificationRegistryError(str(exc)) from exc
        if len(plan.development_years) < plan.thresholds.minimum_development_years:
            raise QualificationRegistryError("historical plan has insufficient development years")
        if len(plan.folds) < plan.thresholds.minimum_evaluation_folds:
            raise QualificationRegistryError("historical plan has insufficient evaluation folds")
        _validate_plan_role_calendar(plan)
        _validate_plan_selection_boundaries(plan)
        if plan.evidence_role in RETROSPECTIVE_EVIDENCE_ROLES and plan.evidence_audit is None:
            raise QualificationRegistryError("retrospective plan requires clean-evidence audit")
        if (
            plan.evidence_role
            in {
                "study-time-retrospective",
                "fixed-calendar-retrospective",
            }
            and plan.study_identity is None
        ):
            raise QualificationRegistryError("study-time plan requires exact frozen study linkage")
        if (
            plan.evidence_role == "historical"
            and plan.evidence_audit is not None
            and (
                plan.evidence_audit.classification != "verified-clean"
                or not plan.evidence_audit.trial_history_complete
            )
        ):
            raise QualificationRegistryError(
                "Historical Evaluation requires verified-clean complete provenance"
            )
        event_id = f"historical-plan:{plan.plan_id}"
        selection_boundary = plan.forward_selection_epoch or plan.retrospective_selection_checkpoint
        if selection_boundary is not None:
            with locked_file(self.lock_path, self.lock_timeout_seconds):
                state = self._load_unlocked()
                self._validate_plan_state_for_registration(state, plan, event_id)

    def _validate_plan_state_for_registration(
        self,
        state: Mapping[str, object],
        plan: HistoricalQualificationPlan,
        event_id: str,
    ) -> None:
        existing = next(
            (event for event in _events(state) if event.get("event_id") == event_id),
            None,
        )
        if existing is None:
            recorded_at = self.now()
            if recorded_at.tzinfo is None:
                raise QualificationRegistryError(
                    "qualification registry clock must be timezone-aware"
                )
            elapsed = abs((recorded_at.astimezone(UTC) - plan.created_at).total_seconds())
            if elapsed > 5:
                raise QualificationRegistryError(
                    "selection plan must be registered when its trial universe freezes"
                )
        projection_events = self._global_plan_projection_events(state)
        open_plan_ids = {
            event_payload.get("plan_id")
            for event in projection_events
            if event.get("event_type") == "historical_plan"
            and isinstance((event_payload := event.get("payload")), Mapping)
            and event_payload.get("experiment_family") == plan.experiment_family
            and not any(
                terminal.get("event_type")
                in {
                    "historical_screen",
                    "historical_plan_abandoned",
                    "historical_plan_closed_invalidated",
                }
                and isinstance(terminal.get("payload"), Mapping)
                and terminal["payload"].get("plan_id") == event_payload.get("plan_id")
                for terminal in projection_events
            )
        }
        if open_plan_ids - {plan.plan_id}:
            raise QualificationRegistryError(
                "experiment family already has an open forward or retrospective qualification plan"
            )

    def _global_plan_projection_events(
        self,
        state: dict[str, object],
    ) -> list[dict[str, object]]:
        """Include immutable shared shards when this registry is the active chain."""
        catalog_path = self.path.parent.parent / "catalog.json"
        if self.path.parent.name != "active" or not catalog_path.is_file():
            return _events(state)
        try:
            catalog = json.loads(catalog_path.read_bytes())
        except (OSError, json.JSONDecodeError) as exc:
            raise QualificationRegistryError(
                f"cannot read shared authority catalog: {exc}"
            ) from exc
        shards = catalog.get("shards") if isinstance(catalog, Mapping) else None
        if not isinstance(shards, list):
            raise QualificationRegistryError("shared authority catalog shards are malformed")
        projected: list[dict[str, object]] = []
        seen_plan_ids: set[str] = set()
        for raw_shard in shards:
            if not isinstance(raw_shard, Mapping):
                raise QualificationRegistryError("shared authority catalog shard is malformed")
            digest = _required_sha256(raw_shard.get("registry_sha256"), "shared shard digest")
            shard_path = self.path.parent.parent / "shards" / digest / "qualification-registry.json"
            shard_events = _events(QualificationRegistry(shard_path).read())
            for event in shard_events:
                if event.get("event_type") == "historical_plan":
                    plan_id = _payload(event).get("plan_id")
                    if not isinstance(plan_id, str) or plan_id in seen_plan_ids:
                        raise QualificationRegistryError(
                            "shared qualification shards contain duplicate plan identities"
                        )
                    seen_plan_ids.add(plan_id)
            projected.extend(shard_events)
        for event in _events(state):
            if event.get("event_type") == "historical_plan":
                plan_id = _payload(event).get("plan_id")
                if not isinstance(plan_id, str) or plan_id in seen_plan_ids:
                    raise QualificationRegistryError(
                        "shared active chain repeats an imported plan identity"
                    )
                seen_plan_ids.add(plan_id)
            projected.append(event)
        return projected

    def abandon_historical_plan(
        self,
        plan_id: str,
        *,
        approved_by: str,
        reason: str,
        study_identity_resolver: Callable[[str], Mapping[str, str]],
        authorization: Mapping[str, str],
    ) -> str:
        """Append an administrative terminal event for a cancelled study's open plan."""
        plan_identity = _required_text(plan_id, "historical plan identity")
        approver = _required_text(approved_by, "qualification plan abandonment approver")
        concrete_reason = _required_text(reason, "qualification plan abandonment reason")
        abandoned_at = self.now()
        if abandoned_at.tzinfo is None or abandoned_at.utcoffset() is None:
            raise QualificationRegistryError(
                "qualification plan abandonment clock must be timezone-aware"
            )
        abandoned_at = abandoned_at.astimezone(UTC)
        authority = _validated_abandonment_authority(authorization)
        event_id = f"historical-plan-abandoned:{plan_identity}"
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            events = _events(state)
            plan_event = _event_for_identity(
                state,
                event_type="historical_plan",
                identity_name="plan_id",
                identity=plan_identity,
            )
            if any(
                event.get("event_type") == "historical_screen"
                and _payload(event).get("plan_id") == plan_identity
                for event in events
            ):
                raise QualificationRegistryError("screened historical plan cannot be abandoned")
            if any(
                event.get("event_type") == "historical_plan_abandoned"
                and _payload(event).get("plan_id") == plan_identity
                for event in events
            ):
                raise QualificationRegistryError("historical plan already has an abandonment event")
            plan_payload = _payload(plan_event)
            study_identity = plan_payload.get("study_identity")
            if not isinstance(study_identity, Mapping):
                raise QualificationRegistryError(
                    "historical plan abandonment requires exact frozen study binding"
                )
            frozen_study = _validated_frozen_study_identity(study_identity)
            try:
                resolved_study = dict(study_identity_resolver(frozen_study["study_path"]))
            except Exception as exc:  # noqa: BLE001 - external identity boundary fails closed
                raise QualificationRegistryError(
                    f"cannot verify owning study for abandonment: {exc}"
                ) from exc
            expected_study = {
                "study_path": frozen_study["study_path"],
                "workflow": authority["workflow"],
                "workflow_version": _required_text(
                    resolved_study.get("workflow_version"),
                    "owning study workflow version",
                ),
                "status": "cancelled",
            }
            actual_study = {
                field: _required_text(resolved_study.get(field), f"owning study {field}")
                for field in expected_study
            }
            if actual_study != expected_study:
                raise QualificationRegistryError(
                    "historical plan abandonment requires the exact cancelled owning study "
                    "in the authorizing workflow family"
                )
            previous_hash = (
                _required_text(events[-1].get("event_hash"), "qualification registry head hash")
                if events
                else _GENESIS_HASH
            )
            payload: dict[str, object] = {
                "plan_id": plan_identity,
                "experiment_family": _required_text(
                    plan_payload.get("experiment_family"),
                    "historical plan experiment family",
                ),
                "study_identity": frozen_study,
                "study_lifecycle": actual_study,
                "authorization": authority,
                "abandoned_at": timestamp_text(abandoned_at),
                "approved_by": approver,
                "reason": concrete_reason,
                "prior_registry": {
                    "event_count": len(events),
                    "head_hash": previous_hash,
                },
            }
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type="historical_plan_abandoned",
                payload=payload,
            )
        return event_id

    def append_cross_chain_terminal(
        self,
        *,
        event_type: str,
        payload: dict[str, object],
    ) -> str:
        """Append a globally verified imported-plan terminal to the active chain.

        The shared-state writer verifies the referenced immutable shard and canonical study.
        This registry boundary validates the durable event shape, hash chain, and checkpoint.
        """
        plan_id = _required_text(payload.get("plan_id"), "cross-chain plan identity")
        event_prefixes = {
            "historical_plan_abandoned": "historical-plan-abandoned",
            "historical_plan_closed_invalidated": "historical-plan-closed-invalidated",
        }
        prefix = event_prefixes.get(event_type)
        if prefix is None:
            raise QualificationRegistryError("unsupported cross-chain terminal event type")
        event_id = f"{prefix}:{plan_id}"
        self._append(event_id=event_id, event_type=event_type, payload=payload)
        return event_id

    def record_historical_screen(
        self,
        screen: HistoricalScreenResult,
        *,
        evaluated_at: datetime,
    ) -> str:
        """Append one deterministic result for a previously frozen historical plan."""
        if evaluated_at.tzinfo is None:
            raise QualificationRegistryError("historical screen clock must be timezone-aware")
        evaluated_at = evaluated_at.astimezone(UTC)
        event_id = f"historical-screen:{screen.plan_id}"
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            plan_event = _event_for_identity(
                state,
                event_type="historical_plan",
                identity_name="plan_id",
                identity=screen.plan_id,
            )
            plan_payload = _payload(plan_event)
            if any(
                event.get("event_type") == "historical_plan_abandoned"
                and _payload(event).get("plan_id") == screen.plan_id
                for event in _events(state)
            ):
                raise QualificationRegistryError(
                    "abandoned historical plan cannot receive a screen"
                )
            fold_payloads = plan_payload.get("folds")
            if not isinstance(fold_payloads, list) or not fold_payloads:
                raise QualificationRegistryError("historical plan folds are malformed")
            expected_folds = tuple(item.get("fold_id") for item in fold_payloads)
            actual_folds = tuple(fold.fold_id for fold in screen.folds)
            if actual_folds != expected_folds:
                raise QualificationRegistryError("historical screen folds differ from frozen plan")
            last_outcome = fold_payloads[-1].get("outcome_end")
            if not isinstance(last_outcome, str) or evaluated_at.date() <= date.fromisoformat(
                last_outcome
            ):
                raise QualificationRegistryError(
                    "historical screen cannot be recorded before all fold outcomes complete"
                )
            if screen.passed != all(gate.passed for gate in screen.gates):
                raise QualificationRegistryError(
                    "historical screen pass state conflicts with gates"
                )
            if tuple(gate.name for gate in screen.gates) != HISTORICAL_QUALIFICATION_GATE_NAMES:
                raise QualificationRegistryError("historical screen gates are incomplete")
            expected_dispositions = (
                ("retrospectively-supported", "retrospective-screen-failed")
                if plan_payload.get("evidence_role", "historical") in RETROSPECTIVE_EVIDENCE_ROLES
                else ("shadow-eligible", "historical-screen-failed")
            )
            expected_disposition = expected_dispositions[0 if screen.passed else 1]
            if screen.disposition != expected_disposition:
                raise QualificationRegistryError(
                    "qualification screen disposition conflicts with its evidence role"
                )
            payload = _historical_screen_payload(screen, evaluated_at)
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type="historical_screen",
                payload=payload,
            )
        return event_id

    def register_shadow(self, registration: ShadowRegistration) -> str:
        recorded_at = self.now()
        if recorded_at.tzinfo is None:
            raise QualificationRegistryError("qualification registry clock must be timezone-aware")
        recorded_at = recorded_at.astimezone(UTC)
        try:
            self.definition_verifier(
                registration.definition_snapshot_id,
                registration.definition_snapshot_byte_count,
                registration.definition_fingerprint,
            )
        except Exception as exc:  # noqa: BLE001 - immutable evidence boundary fails closed
            raise QualificationRegistryError(
                f"Shadow definition snapshot cannot be verified: {exc}"
            ) from exc
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            event_id = f"shadow-registration:{registration.shadow_id}"
            existing = next(
                (event for event in _events(state) if event.get("event_id") == event_id),
                None,
            )
            if existing is not None:
                existing_recorded_at = _payload(existing).get("recorded_at")
                if not isinstance(existing_recorded_at, str):
                    raise QualificationRegistryError("Shadow registration time is malformed")
                recorded_at = parse_timestamp(existing_recorded_at)
            elif recorded_at != registration.prospective_start:
                raise QualificationRegistryError(
                    "Shadow prospective start must match formal registry time"
                )
            payload = _registration_payload(registration, recorded_at=recorded_at)
            plan_event = _event_for_identity(
                state,
                event_type="historical_plan",
                identity_name="plan_id",
                identity=registration.historical_plan_id,
            )
            screen_event = _event_for_identity(
                state,
                event_type="historical_screen",
                identity_name="plan_id",
                identity=registration.historical_plan_id,
            )
            plan_payload = _payload(plan_event)
            screen_payload = _payload(screen_event)
            selection = screen_payload.get("selection_adjustment")
            evaluated_at = screen_payload.get("evaluated_at")
            if (
                plan_payload.get("evidence_role", "historical") != "historical"
                or plan_payload.get("experiment_family") != registration.experiment_family
                or plan_payload.get("definition_fingerprint") != registration.definition_fingerprint
                or plan_payload.get("cost_policies")
                != _cost_policy_payload(
                    registration.base_cost_policy,
                    registration.stress_cost_policy,
                )
                or screen_payload.get("passed") is not True
                or screen_payload.get("disposition") != "shadow-eligible"
                or not isinstance(selection, Mapping)
                or selection.get("selected_trial_id") != registration.trial_id
                or not isinstance(evaluated_at, str)
                or registration.prospective_start <= parse_timestamp(evaluated_at)
            ):
                raise QualificationRegistryError(
                    "Shadow registration conflicts with historical qualification evidence"
                )
            if registration.prior_shadow_id is not None:
                _registration_event(state, registration.prior_shadow_id)
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type="shadow_registration",
                payload=payload,
            )
        return registration.shadow_id

    def record_shadow_evidence(self, evidence: ShadowEvidence) -> str:
        proposal_ids = tuple(proposal.proposal_id for proposal in evidence.paper_proposals)
        fill_ids = tuple(fill.proposal_id for fill in evidence.simulated_fills)
        if len(set(proposal_ids)) != len(proposal_ids) or len(set(fill_ids)) != len(fill_ids):
            raise QualificationRegistryError("Shadow proposal and fill identities must be unique")
        if any(proposal.shadow_id != evidence.shadow_id for proposal in evidence.paper_proposals):
            raise QualificationRegistryError("Shadow proposal belongs to a different registration")
        if not set(fill_ids).issubset(proposal_ids):
            raise QualificationRegistryError("canonical simulated fill has no Shadow proposal")
        if evidence.completed_sessions < 0:
            raise QualificationRegistryError("Shadow completed sessions cannot be negative")
        if evidence.data_cutoff < evidence.as_of:
            raise QualificationRegistryError("Shadow data cutoff predates its checkpoint")
        numeric_values = (
            evidence.cumulative_return,
            evidence.stress_cumulative_return,
            evidence.stress_max_drawdown,
            *(
                value
                for fill in evidence.simulated_fills
                for value in (
                    fill.quantity,
                    fill.executed_entry_price,
                    fill.executed_exit_price,
                    fill.pnl,
                )
            ),
        )
        if any(not math.isfinite(value) for value in numeric_values):
            raise QualificationRegistryError("Shadow evidence metrics must be finite")
        if any(
            fill.quantity <= 0 or fill.executed_entry_price <= 0 or fill.executed_exit_price <= 0
            for fill in evidence.simulated_fills
        ):
            raise QualificationRegistryError("canonical simulated fill terms must be positive")
        event_id = f"shadow-evidence:{evidence.shadow_id}:{evidence.as_of.isoformat()}"
        payload = _evidence_payload(evidence)
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            registration = _registration_event(state, evidence.shadow_id)
            registered_payload = registration["payload"]
            if not isinstance(registered_payload, Mapping):  # pragma: no cover - validated on read
                raise QualificationRegistryError("qualification registration payload is malformed")
            if registered_payload.get("definition_fingerprint") != evidence.definition_fingerprint:
                raise QualificationRegistryError("Shadow evidence changed frozen definition")
            prospective_start = registered_payload.get("prospective_start")
            if not isinstance(prospective_start, str) or evidence.as_of <= date.fromisoformat(
                prospective_start[:10]
            ):
                raise QualificationRegistryError("Shadow evidence predates formal registration")
            prospective_date = date.fromisoformat(prospective_start[:10])
            if any(
                proposal.signal_date <= prospective_date
                or proposal.signal_date > evidence.as_of
                or proposal.entry_date < proposal.signal_date
                or proposal.entry_date > evidence.data_cutoff
                for proposal in evidence.paper_proposals
            ):
                raise QualificationRegistryError(
                    "Shadow paper proposal dates fall outside prospective evidence"
                )
            prior_evidence = [
                event
                for event in _events(state)
                if event.get("event_type") == "shadow_evidence"
                and isinstance(event.get("payload"), Mapping)
                and event["payload"].get("shadow_id") == evidence.shadow_id
            ]
            if prior_evidence:
                previous = _payload(prior_evidence[-1])
                previous_as_of = date.fromisoformat(str(previous.get("as_of")))
                if evidence.as_of < previous_as_of:
                    raise QualificationRegistryError(
                        "Shadow evidence checkpoints cannot go backward"
                    )
                if evidence.as_of > previous_as_of:
                    previous_cutoff = date.fromisoformat(str(previous.get("data_cutoff")))
                    if evidence.data_cutoff < previous_cutoff:
                        raise QualificationRegistryError("Shadow data cutoff cannot decrease")
                    if evidence.completed_sessions < int(previous.get("completed_sessions", -1)):
                        raise QualificationRegistryError(
                            "Shadow evidence completed sessions cannot decrease"
                        )
                    _require_history_prefix(
                        previous.get("paper_proposals"),
                        payload["paper_proposals"],
                        "paper proposal",
                    )
                    previous_proposals = previous.get("paper_proposals")
                    if not isinstance(previous_proposals, list):
                        raise QualificationRegistryError(
                            "Shadow paper proposal history is malformed"
                        )
                    for proposal in payload["paper_proposals"][len(previous_proposals) :]:
                        if (
                            not isinstance(proposal, Mapping)
                            or date.fromisoformat(str(proposal.get("signal_date")))
                            <= previous_as_of
                        ):
                            raise QualificationRegistryError(
                                "Shadow paper proposals cannot backfill a prior checkpoint"
                            )
                    _require_history_prefix(
                        previous.get("simulated_fills"),
                        payload["simulated_fills"],
                        "simulated fill",
                    )
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type="shadow_evidence",
                payload=payload,
            )
        return event_id

    def record_activation_evaluation(
        self,
        evaluation: ShadowActivationEvaluation,
        *,
        evaluated_at: date,
    ) -> str:
        event_id = f"activation-evaluation:{evaluation.shadow_id}:{evaluated_at.isoformat()}"
        payload = _activation_payload(evaluation, evaluated_at)
        gates_passed = bool(evaluation.gates) and all(gate.passed for gate in evaluation.gates)
        if tuple(gate.name for gate in evaluation.gates) != SHADOW_ACTIVATION_GATE_NAMES:
            raise QualificationRegistryError("activation evaluation gates are incomplete")
        if evaluation.eligible != gates_passed:
            raise QualificationRegistryError("activation eligibility conflicts with its gates")
        if (evaluation.disposition == "activation-eligible") != evaluation.eligible:
            raise QualificationRegistryError("activation disposition conflicts with its gates")
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            _registration_event(state, evaluation.shadow_id)
            evidence = next(
                (
                    event
                    for event in _events(state)
                    if event.get("event_type") == "shadow_evidence"
                    and isinstance(event.get("payload"), Mapping)
                    and event["payload"].get("shadow_id") == evaluation.shadow_id
                    and event["payload"].get("as_of") == evaluated_at.isoformat()
                ),
                None,
            )
            if evidence is None:
                raise QualificationRegistryError(
                    "activation evaluation requires matching prospective evidence"
                )
            registration = _registration_event(state, evaluation.shadow_id)
            registration_payload = _payload(registration)
            try:
                current_definition_fingerprint = self.current_definition_resolver(
                    str(registration_payload.get("experiment_family")),
                    str(registration_payload.get("trial_id")),
                )
            except Exception as exc:  # noqa: BLE001 - current-definition boundary fails closed
                raise QualificationRegistryError(
                    f"current Shadow definition cannot be verified: {exc}"
                ) from exc
            _validate_activation_gate_results(
                evaluation,
                registration=registration_payload,
                evidence=_payload(evidence),
                current_definition_fingerprint=current_definition_fingerprint,
            )
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type="activation_evaluation",
                payload=payload,
            )
        return event_id

    def _append(self, *, event_id: str, event_type: str, payload: dict[str, object]) -> None:
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked()
            self._append_unlocked(
                state,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
            )

    def _append_unlocked(
        self,
        state: dict[str, object],
        *,
        event_id: str,
        event_type: str,
        payload: dict[str, object],
    ) -> None:
        try:
            json.dumps(payload, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise QualificationRegistryError(
                "qualification event payload must contain finite JSON values"
            ) from exc
        events = _events(state)
        if events and not all("event_hash" in event for event in events):
            raise QualificationRegistryError(
                "legacy qualification registry must be imported before appending"
            )
        existing = next((event for event in events if event.get("event_id") == event_id), None)
        if existing is not None:
            if existing.get("event_type") != event_type or existing.get("payload") != payload:
                raise QualificationRegistryError(
                    f"qualification event {event_id} conflicts with history"
                )
            return
        events.append(
            _chained_event(
                sequence=len(events) + 1,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                previous_hash=(
                    events[-1].get("event_hash", _GENESIS_HASH) if events else _GENESIS_HASH
                ),
            )
        )
        content = canonical_json_bytes(state)
        atomic_write(self.path, content, replace=True)
        _write_head_checkpoint(self.checkpoint_path, content, events)

    def _load_unlocked(self) -> dict[str, object]:
        if not self.path.exists():
            return {
                "schema_version": QUALIFICATION_REGISTRY_SCHEMA_VERSION,
                "events": [],
            }
        try:
            content = self.path.read_bytes()
            state = json.loads(content)
        except (OSError, json.JSONDecodeError) as exc:
            raise QualificationRegistryError(f"cannot read qualification registry: {exc}") from exc
        if not isinstance(state, dict):
            raise QualificationRegistryError("qualification registry must be a JSON object")
        if state.get("schema_version") != QUALIFICATION_REGISTRY_SCHEMA_VERSION:
            raise QualificationRegistryError("unsupported qualification registry schema")
        events = _events(state)
        for sequence, event in enumerate(events, start=1):
            if (
                event.get("sequence") != sequence
                or not isinstance(event.get("event_id"), str)
                or not isinstance(event.get("event_type"), str)
                or not isinstance(event.get("payload"), dict)
            ):
                raise QualificationRegistryError("qualification registry event is malformed")
        if len({event["event_id"] for event in events}) != len(events):
            raise QualificationRegistryError("qualification registry contains duplicate events")
        try:
            json.dumps(state, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise QualificationRegistryError(
                "qualification registry contains non-finite JSON values"
            ) from exc
        _validate_lifecycle(events)
        _validate_hash_chain(events)
        _verify_head_checkpoint(self.checkpoint_path, content, events)
        self._verify_definition_snapshots(events)
        return state

    def _verify_definition_snapshots(self, events: list[dict[str, object]]) -> None:
        for event in events:
            if event.get("event_type") != "shadow_registration":
                continue
            payload = _payload(event)
            digest = payload.get("definition_snapshot_id")
            byte_count = payload.get("definition_snapshot_byte_count")
            fingerprint = payload.get("definition_fingerprint")
            if (
                not isinstance(digest, str)
                or not isinstance(byte_count, int)
                or not isinstance(fingerprint, str)
            ):
                raise QualificationRegistryError("Shadow definition snapshot identity is malformed")
            try:
                self.definition_verifier(digest, byte_count, fingerprint)
            except Exception as exc:  # noqa: BLE001 - immutable evidence boundary fails closed
                raise QualificationRegistryError(
                    f"Shadow definition snapshot cannot be verified: {exc}"
                ) from exc


def _events(state: dict[str, object]) -> list[dict[str, object]]:
    events = state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise QualificationRegistryError("qualification registry events are malformed")
    return events


def _chained_event(
    *,
    sequence: int,
    event_id: str,
    event_type: str,
    payload: dict[str, object],
    previous_hash: object,
) -> dict[str, object]:
    if not isinstance(previous_hash, str):
        raise QualificationRegistryError("qualification event previous hash is malformed")
    content = {
        "sequence": sequence,
        "event_id": event_id,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": previous_hash,
    }
    return {
        **content,
        "event_hash": hashlib.sha256(canonical_json_bytes(content)).hexdigest(),
    }


def _validate_hash_chain(events: list[dict[str, object]]) -> None:
    if not events:
        return
    if not all("event_hash" in event and "previous_hash" in event for event in events):
        raise QualificationRegistryError("qualification registry hash chain is incomplete")
    previous_hash = _GENESIS_HASH
    for event in events:
        if event.get("previous_hash") != previous_hash:
            raise QualificationRegistryError("qualification registry hash chain is broken")
        content = {
            "sequence": event.get("sequence"),
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "payload": event.get("payload"),
            "previous_hash": event.get("previous_hash"),
        }
        expected = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        if event.get("event_hash") != expected:
            raise QualificationRegistryError("qualification registry event hash is invalid")
        previous_hash = expected


def _write_head_checkpoint(
    path: Path,
    content: bytes,
    events: list[dict[str, object]],
) -> None:
    payload = {
        "schema_version": 1,
        "event_count": len(events),
        "registry_checksum": hashlib.sha256(content).hexdigest(),
        "head_hash": events[-1]["event_hash"] if events else _GENESIS_HASH,
    }
    atomic_write(path, canonical_json_bytes(payload), replace=True)


def _verify_head_checkpoint(
    path: Path,
    content: bytes,
    events: list[dict[str, object]],
) -> None:
    try:
        payload = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise QualificationRegistryError(
            "qualification registry head checkpoint is missing or invalid"
        ) from exc
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 1
        or payload.get("event_count") != len(events)
        or payload.get("registry_checksum") != hashlib.sha256(content).hexdigest()
        or payload.get("head_hash") != (events[-1].get("event_hash") if events else _GENESIS_HASH)
    ):
        raise QualificationRegistryError(
            "qualification registry head checkpoint does not match history"
        )


def _require_history_prefix(previous: object, current: object, label: str) -> None:
    if not isinstance(previous, list) or not isinstance(current, list):
        raise QualificationRegistryError(f"Shadow {label} history is malformed")
    if current[: len(previous)] != previous:
        raise QualificationRegistryError(f"Shadow {label} history cannot be rewritten")


def _validate_activation_gate_results(
    evaluation: ShadowActivationEvaluation,
    *,
    registration: Mapping[str, object],
    evidence: Mapping[str, object],
    current_definition_fingerprint: str,
) -> None:
    policy = registration.get("activation_policy")
    fills = evidence.get("simulated_fills")
    if not isinstance(policy, Mapping) or not isinstance(fills, list):
        raise QualificationRegistryError("activation source evidence is malformed")
    gates = {gate.name: gate for gate in evaluation.gates}
    try:
        expected = {
            "shadow_identity": evidence.get("shadow_id") == registration.get("shadow_id"),
            "definition_unchanged": (
                current_definition_fingerprint == registration.get("definition_fingerprint")
                and evidence.get("definition_fingerprint")
                == registration.get("definition_fingerprint")
                and gates["definition_unchanged"].actual == current_definition_fingerprint
            ),
            "activation_checkpoint": date.fromisoformat(str(evidence.get("as_of")))
            >= date.fromisoformat(str(registration.get("activation_checkpoint"))),
            "completed_sessions": int(evidence.get("completed_sessions", -1))
            >= int(policy.get("minimum_completed_sessions", -1)),
            "completed_trades": len(fills) >= int(policy.get("minimum_completed_trades", -1)),
            "prospective_cumulative_return": _registry_decimal(evidence.get("cumulative_return"))
            > _registry_decimal(policy.get("minimum_cumulative_return")),
            "prospective_profit_factor": _registry_decimal(evidence.get("profit_factor"))
            > _registry_decimal(policy.get("minimum_profit_factor")),
            "stress_cumulative_return": _registry_decimal(evidence.get("stress_cumulative_return"))
            > _registry_decimal(policy.get("minimum_stress_cumulative_return")),
            "stress_profit_factor": _registry_decimal(evidence.get("stress_profit_factor"))
            > _registry_decimal(policy.get("minimum_stress_profit_factor")),
            "stress_drawdown": _registry_decimal(evidence.get("stress_max_drawdown"))
            >= -_registry_decimal(policy.get("stress_drawdown_limit")),
            "critical_drift": evidence.get("critical_drift") is False,
        }
    except (TypeError, ValueError, InvalidOperation) as exc:
        raise QualificationRegistryError("activation source evidence is malformed") from exc
    if any(gates[name].passed != expected[name] for name in SHADOW_ACTIVATION_GATE_NAMES):
        raise QualificationRegistryError("activation gates conflict with prospective evidence")


def _registry_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def _missing_current_definition(_experiment_family: str, _trial_id: str) -> str:
    raise QualificationRegistryError("no current-definition resolver is configured")


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise QualificationRegistryError(f"{label} is missing or non-canonical")
    return value


def _required_sha256(value: object, label: str) -> str:
    digest = _required_text(value, label)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise QualificationRegistryError(f"{label} is not a canonical SHA-256 digest")
    return digest


def _required_repository_path(value: object, label: str) -> str:
    text = _required_text(value, label)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != text:
        raise QualificationRegistryError(f"{label} is not a safe repository-relative path")
    return text


def _validated_frozen_study_identity(identity: Mapping[str, object]) -> dict[str, str]:
    return {
        "study_path": _required_repository_path(identity.get("study_path"), "frozen study path"),
        "preregistration_sha256": _required_sha256(
            identity.get("preregistration_sha256"),
            "frozen preregistration identity",
        ),
        "plan_sha256": _required_sha256(identity.get("plan_sha256"), "frozen plan identity"),
        "candidate_freeze_sha256": _required_sha256(
            identity.get("candidate_freeze_sha256"),
            "candidate freeze identity",
        ),
        "qualification_spec_sha256": _required_sha256(
            identity.get("qualification_spec_sha256"),
            "qualification specification identity",
        ),
        "workflow_release_sha256": _required_sha256(
            identity.get("workflow_release_sha256"),
            "owning workflow release identity",
        ),
    }


def _validated_abandonment_authority(authority: Mapping[str, object]) -> dict[str, str]:
    payload = {
        "workflow": _required_text(authority.get("workflow"), "authorizing workflow"),
        "workflow_version": _required_text(
            authority.get("workflow_version"),
            "authorizing workflow version",
        ),
        "workflow_path": _required_repository_path(
            authority.get("workflow_path"),
            "authorizing workflow path",
        ),
        "workflow_release_sha256": _required_sha256(
            authority.get("workflow_release_sha256"),
            "authorizing workflow release identity",
        ),
        "capability": _required_text(
            authority.get("capability"),
            "qualification plan abandonment capability",
        ),
    }
    if payload["capability"] != QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY:
        raise QualificationRegistryError(
            "authorization does not grant qualification-plan abandonment"
        )
    if Path(payload["workflow_path"]).name != (
        f"{payload['workflow']}--{payload['workflow_version']}"
    ):
        raise QualificationRegistryError(
            "authorizing workflow path, family, and version are inconsistent"
        )
    return payload


def _validate_cross_chain_terminal(
    event: Mapping[str, object],
    *,
    expected_status: str,
) -> None:
    payload = _payload(dict(event))
    plan_id = _required_text(payload.get("plan_id"), "cross-chain plan identity")
    _required_text(payload.get("experiment_family"), "cross-chain experiment family")
    binding = payload.get("source_binding")
    study_identity = payload.get("study_identity")
    lifecycle = payload.get("study_lifecycle")
    authority = payload.get("authorization")
    impact = payload.get("accepted_impact")
    prior_shared = payload.get("prior_shared")
    if not all(
        isinstance(item, Mapping)
        for item in (binding, study_identity, lifecycle, authority, impact, prior_shared)
    ):
        raise QualificationRegistryError("cross-chain terminal authority is malformed")
    if binding.get("plan_id") != plan_id:
        raise QualificationRegistryError("cross-chain source binding uses a different plan")
    for field in ("registry_sha256", "head_hash", "plan_event_hash"):
        _required_sha256(binding.get(field), f"cross-chain source {field}")
    frozen_study = _validated_frozen_study_identity(study_identity)
    if (
        lifecycle.get("study_path") != frozen_study["study_path"]
        or lifecycle.get("status") != expected_status
        or not isinstance(lifecycle.get("workflow"), str)
        or not isinstance(lifecycle.get("workflow_version"), str)
    ):
        raise QualificationRegistryError("cross-chain terminal study lifecycle is inconsistent")
    capabilities = authority.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(capability, str) and capability for capability in capabilities
    ):
        raise QualificationRegistryError("cross-chain authorization capabilities are malformed")
    required_capabilities = {
        "shared-qualification-state-v1",
        "cross-chain-plan-administration-v1",
    }
    if expected_status == "cancelled":
        required_capabilities.add("qualification-plan-abandonment-v1")
    if not required_capabilities.issubset(capabilities):
        raise QualificationRegistryError("cross-chain authorization lacks required capabilities")
    _required_text(authority.get("workflow"), "cross-chain authorizing workflow")
    _required_text(authority.get("workflow_version"), "cross-chain authorizing version")
    _required_repository_path(authority.get("workflow_path"), "cross-chain workflow path")
    _required_sha256(
        authority.get("workflow_release_sha256"),
        "cross-chain workflow release identity",
    )
    _required_repository_path(impact.get("path"), "accepted impact path")
    _required_sha256(impact.get("impact_sha256"), "accepted impact identity")
    _required_sha256(impact.get("decision_sha256"), "accepted decision identity")
    expected_disposition = "cancelled" if expected_status == "cancelled" else "close-invalidated"
    if impact.get("disposition") != expected_disposition:
        raise QualificationRegistryError("accepted impact disposition is invalid")
    _required_sha256(prior_shared.get("catalog_sha256"), "prior shared catalog identity")
    if (
        not isinstance(prior_shared.get("active_event_count"), int)
        or prior_shared.get("active_event_count") != event.get("sequence", 0) - 1
        or prior_shared.get("active_head_hash") != event.get("previous_hash")
    ):
        raise QualificationRegistryError("prior shared active-chain identity is malformed")
    recorded_at = _required_text(payload.get("recorded_at"), "cross-chain terminal time")
    try:
        if timestamp_text(parse_timestamp(recorded_at)) != recorded_at:
            raise ValueError("non-canonical timestamp")
    except ValueError as exc:
        raise QualificationRegistryError("cross-chain terminal time is malformed") from exc
    _required_text(payload.get("approved_by"), "cross-chain terminal approver")
    _required_text(payload.get("reason"), "cross-chain terminal reason")


def _validate_lifecycle(events: list[dict[str, object]]) -> None:
    plans: dict[str, Mapping[str, object]] = {}
    screens: set[str] = set()
    abandoned: set[str] = set()
    shadows: set[str] = set()
    evidence_dates: set[tuple[str, str]] = set()
    for event in events:
        event_type = event["event_type"]
        payload = _payload(event)
        if event_type == "historical_plan":
            plan_id = payload.get("plan_id")
            if not isinstance(plan_id, str) or not plan_id:
                raise QualificationRegistryError("historical plan identity is malformed")
            if event.get("event_id") != f"historical-plan:{plan_id}":
                raise QualificationRegistryError("historical plan event identity is not canonical")
            if plan_id in plans:
                raise QualificationRegistryError("qualification registry repeats a historical plan")
            plans[plan_id] = payload
        elif event_type == "historical_screen":
            plan_id = payload.get("plan_id")
            if plan_id not in plans:
                raise QualificationRegistryError("historical screen precedes its frozen plan")
            if plan_id in abandoned:
                raise QualificationRegistryError("abandoned historical plan has a later screen")
            if event.get("event_id") != f"historical-screen:{plan_id}":
                raise QualificationRegistryError(
                    "historical screen event identity is not canonical"
                )
            if plan_id in screens:
                raise QualificationRegistryError(
                    "qualification registry repeats a historical screen"
                )
            screens.add(plan_id)
        elif event_type == "historical_plan_abandoned":
            plan_id = payload.get("plan_id")
            imported = isinstance(payload.get("source_binding"), Mapping)
            if not isinstance(plan_id, str) or (plan_id not in plans and not imported):
                raise QualificationRegistryError(
                    "historical plan abandonment precedes its frozen plan"
                )
            if event.get("event_id") != f"historical-plan-abandoned:{plan_id}":
                raise QualificationRegistryError(
                    "historical plan abandonment event identity is not canonical"
                )
            if plan_id in screens:
                raise QualificationRegistryError("screened historical plan is later abandoned")
            if plan_id in abandoned:
                raise QualificationRegistryError(
                    "qualification registry repeats a historical plan abandonment"
                )
            if imported:
                _validate_cross_chain_terminal(event, expected_status="cancelled")
                abandoned.add(plan_id)
                continue
            plan_payload = plans[plan_id]
            if payload.get("experiment_family") != plan_payload.get("experiment_family"):
                raise QualificationRegistryError(
                    "historical plan abandonment family differs from its frozen plan"
                )
            plan_study = plan_payload.get("study_identity")
            event_study = payload.get("study_identity")
            if not isinstance(plan_study, Mapping) or not isinstance(event_study, Mapping):
                raise QualificationRegistryError(
                    "historical plan abandonment lacks exact frozen study binding"
                )
            if _validated_frozen_study_identity(event_study) != _validated_frozen_study_identity(
                plan_study
            ):
                raise QualificationRegistryError(
                    "historical plan abandonment study identity differs from its frozen plan"
                )
            lifecycle = payload.get("study_lifecycle")
            authorization = payload.get("authorization")
            if not isinstance(lifecycle, Mapping) or not isinstance(authorization, Mapping):
                raise QualificationRegistryError(
                    "historical plan abandonment authority is malformed"
                )
            authority = _validated_abandonment_authority(authorization)
            if (
                lifecycle.get("study_path") != event_study.get("study_path")
                or lifecycle.get("workflow") != authority["workflow"]
                or lifecycle.get("status") != "cancelled"
                or not isinstance(lifecycle.get("workflow_version"), str)
                or not lifecycle.get("workflow_version")
            ):
                raise QualificationRegistryError(
                    "historical plan abandonment does not bind an exact cancelled owning study"
                )
            abandoned_at = _required_text(
                payload.get("abandoned_at"),
                "historical plan abandonment time",
            )
            try:
                if timestamp_text(parse_timestamp(abandoned_at)) != abandoned_at:
                    raise ValueError("non-canonical timestamp")
            except ValueError as exc:
                raise QualificationRegistryError(
                    "historical plan abandonment time is malformed"
                ) from exc
            _required_text(payload.get("approved_by"), "historical plan abandonment approver")
            _required_text(payload.get("reason"), "historical plan abandonment reason")
            prior_registry = payload.get("prior_registry")
            if (
                not isinstance(prior_registry, Mapping)
                or prior_registry.get("event_count") != event.get("sequence", 0) - 1
                or prior_registry.get("head_hash") != event.get("previous_hash")
            ):
                raise QualificationRegistryError(
                    "historical plan abandonment prior registry identity is malformed"
                )
            abandoned.add(plan_id)
        elif event_type == "historical_plan_closed_invalidated":
            plan_id = payload.get("plan_id")
            if not isinstance(plan_id, str) or not isinstance(
                payload.get("source_binding"), Mapping
            ):
                raise QualificationRegistryError(
                    "invalidated plan closure requires an imported source binding"
                )
            if event.get("event_id") != f"historical-plan-closed-invalidated:{plan_id}":
                raise QualificationRegistryError(
                    "invalidated plan closure event identity is not canonical"
                )
            if plan_id in screens or plan_id in abandoned:
                raise QualificationRegistryError("historical plan already has a terminal event")
            _validate_cross_chain_terminal(event, expected_status="paused")
            abandoned.add(plan_id)
        elif event_type == "shadow_registration":
            shadow_id = payload.get("shadow_id")
            plan_id = payload.get("historical_plan_id")
            if (
                not isinstance(shadow_id, str)
                or plan_id not in plans
                or plan_id not in screens
                or plan_id in abandoned
            ):
                raise QualificationRegistryError(
                    "Shadow registration precedes passing historical evidence"
                )
            shadows.add(shadow_id)
        elif event_type == "shadow_evidence":
            shadow_id = payload.get("shadow_id")
            as_of = payload.get("as_of")
            if shadow_id not in shadows or not isinstance(as_of, str):
                raise QualificationRegistryError("Shadow evidence precedes registration")
            evidence_dates.add((shadow_id, as_of))
        elif event_type == "activation_evaluation":
            shadow_id = payload.get("shadow_id")
            evaluated_at = payload.get("evaluated_at")
            if (shadow_id, evaluated_at) not in evidence_dates:
                raise QualificationRegistryError(
                    "activation evaluation precedes matching Shadow evidence"
                )
        else:
            raise QualificationRegistryError(
                f"qualification registry event type is unknown: {event_type}"
            )


def _registration_event(state: dict[str, object], shadow_id: str) -> dict[str, object]:
    event = next(
        (
            item
            for item in _events(state)
            if item.get("event_type") == "shadow_registration"
            and isinstance(item.get("payload"), Mapping)
            and item["payload"].get("shadow_id") == shadow_id
        ),
        None,
    )
    if event is None:
        raise QualificationRegistryError(f"Shadow is not registered: {shadow_id}")
    return event


def _event_for_identity(
    state: dict[str, object],
    *,
    event_type: str,
    identity_name: str,
    identity: str,
) -> dict[str, object]:
    event = next(
        (
            item
            for item in _events(state)
            if item.get("event_type") == event_type
            and isinstance(item.get("payload"), Mapping)
            and item["payload"].get(identity_name) == identity
        ),
        None,
    )
    if event is None:
        raise QualificationRegistryError(f"qualification event is missing: {event_type}:{identity}")
    return event


def _payload(event: dict[str, object]) -> Mapping[str, object]:
    payload = event.get("payload")
    if not isinstance(payload, Mapping):  # pragma: no cover - registry read validates this
        raise QualificationRegistryError("qualification event payload is malformed")
    return payload


def _validate_plan_role_calendar(plan: HistoricalQualificationPlan) -> None:
    expected_legacy_years = tuple(
        range(
            plan.folds[0].evaluation_year - plan.thresholds.minimum_development_years,
            plan.folds[0].evaluation_year,
        )
    )
    calendar = plan.role_calendar
    if calendar is None:
        legacy_chronology = (
            set(expected_legacy_years).issubset(plan.development_years)
            and max(plan.development_years) < plan.folds[0].evaluation_year
        )
        if not legacy_chronology:
            raise QualificationRegistryError(
                "nonstandard Development chronology requires an explicit role calendar"
            )
        return
    if not calendar.development_sessions or not calendar.warmup_sessions:
        raise QualificationRegistryError("qualification role calendar is incomplete")
    if calendar.evaluation_sessions != plan.evaluation_sessions:
        raise QualificationRegistryError(
            "qualification role calendar evaluation sessions do not match the plan"
        )
    if (
        tuple(sorted(set(calendar.development_sessions))) != calendar.development_sessions
        or tuple(sorted(set(calendar.warmup_sessions))) != calendar.warmup_sessions
        or tuple(sorted(set(calendar.quarantined_sessions))) != calendar.quarantined_sessions
    ):
        raise QualificationRegistryError(
            "qualification role calendar sessions must be unique and chronological"
        )
    development_years = tuple(sorted({session.year for session in calendar.development_sessions}))
    if development_years != plan.development_years:
        raise QualificationRegistryError(
            "qualification role calendar Development years do not match the plan"
        )
    development = set(calendar.development_sessions)
    warmup = set(calendar.warmup_sessions)
    evaluation = set(calendar.evaluation_sessions)
    quarantined = set(calendar.quarantined_sessions)
    if (
        development & warmup
        or development & evaluation
        or warmup & evaluation
        or quarantined & development
        or quarantined & warmup
        or quarantined & evaluation
    ):
        raise QualificationRegistryError("qualification role calendar sessions overlap")
    if calendar.warmup_sessions[-1] >= calendar.evaluation_sessions[0]:
        raise QualificationRegistryError(
            "qualification role calendar warmup must precede evaluation"
        )
    if len(calendar.warmup_sessions) < plan.dependency_sessions:
        raise QualificationRegistryError(
            "qualification role calendar warmup does not cover dependencies"
        )
    if calendar.development_sessions[-1] >= plan.created_at.date():
        raise QualificationRegistryError(
            "qualification role calendar Development context was not complete at plan freeze"
        )
    if plan.evidence_role in {
        "study-time-retrospective",
        "fixed-calendar-retrospective",
    } and (calendar.development_sessions[-1] >= calendar.evaluation_sessions[0]):
        raise QualificationRegistryError(
            "study-time retrospective Development must precede evaluation"
        )
    if plan.evidence_role == "historical" and calendar.quarantined_sessions:
        if (
            calendar.development_sessions[-1] >= calendar.quarantined_sessions[0]
            or calendar.quarantined_sessions[-1] >= calendar.evaluation_sessions[0]
        ):
            raise QualificationRegistryError(
                "clean Historical quarantine must follow Development and precede evaluation"
            )


def _historical_plan_payload(plan: HistoricalQualificationPlan) -> dict[str, object]:
    thresholds = plan.thresholds
    payload: dict[str, object] = {
        "plan_id": plan.plan_id,
        "experiment_family": plan.experiment_family,
        "definition_fingerprint": plan.definition_fingerprint,
        "created_at": timestamp_text(plan.created_at),
        "development_years": list(plan.development_years),
        "evaluation_sessions": [session.isoformat() for session in plan.evaluation_sessions],
        "folds": [
            {
                "fold_id": fold.fold_id,
                "evaluation_year": fold.evaluation_year,
                "outcome_start": fold.outcome_start.isoformat(),
                "outcome_end": fold.outcome_end.isoformat(),
                "signal_start": fold.signal_start.isoformat(),
                "signal_end": fold.signal_end.isoformat(),
            }
            for fold in plan.folds
        ],
        "dependency_sessions": plan.dependency_sessions,
        "embargo_sessions": plan.embargo_sessions,
        "maximum_holding_sessions": plan.maximum_holding_sessions,
        "execution_lag_sessions": plan.execution_lag_sessions,
        "stress_drawdown_limit": decimal_text(plan.stress_drawdown_limit),
        "cost_policies": _cost_policy_payload(
            plan.base_cost_policy,
            plan.stress_cost_policy,
        ),
        "thresholds": {
            "minimum_development_years": thresholds.minimum_development_years,
            "minimum_evaluation_folds": thresholds.minimum_evaluation_folds,
            "minimum_completed_trades": thresholds.minimum_completed_trades,
            "minimum_traded_folds": thresholds.minimum_traded_folds,
            "minimum_positive_fold_rate": decimal_text(thresholds.minimum_positive_fold_rate),
            "minimum_cumulative_return": decimal_text(thresholds.minimum_cumulative_return),
            "minimum_profit_factor": decimal_text(thresholds.minimum_profit_factor),
            "minimum_stress_cumulative_return": decimal_text(
                thresholds.minimum_stress_cumulative_return
            ),
            "minimum_stress_profit_factor": decimal_text(thresholds.minimum_stress_profit_factor),
            "maximum_fold_concentration": decimal_text(thresholds.maximum_fold_concentration),
            "selection_confidence": decimal_text(thresholds.selection_confidence),
        },
        "benchmarks": {
            "family_baseline_trial_id": plan.benchmarks.family_baseline_trial_id,
            "random_seed": plan.benchmarks.random_seed,
            "random_samples": plan.benchmarks.random_samples,
        },
        "selection_adjustment": {
            "repetitions": plan.selection_adjustment.repetitions,
            "block_sessions": plan.selection_adjustment.block_sessions,
        },
    }
    if plan.forward_selection_epoch is not None:
        epoch = plan.forward_selection_epoch
        payload["forward_selection_epoch"] = {
            "started_at": timestamp_text(epoch.started_at),
            "selected_trial_id": epoch.selected_trial_id,
            "included_trial_ids": list(epoch.included_trial_ids),
            "prior_selection_history_incomplete": epoch.prior_selection_history_incomplete,
        }
    if plan.retrospective_selection_checkpoint is not None:
        checkpoint = plan.retrospective_selection_checkpoint
        payload["retrospective_selection_checkpoint"] = {
            "frozen_at": timestamp_text(checkpoint.frozen_at),
            "selected_trial_id": checkpoint.selected_trial_id,
            "included_trial_ids": list(checkpoint.included_trial_ids),
            "prior_selection_history_incomplete": checkpoint.prior_selection_history_incomplete,
        }
    if plan.evidence_audit is not None:
        payload["evidence_role"] = plan.evidence_role
        payload["evidence_audit"] = {
            "classification": plan.evidence_audit.classification,
            "frozen_at": timestamp_text(plan.evidence_audit.frozen_at),
            "justification": plan.evidence_audit.justification,
            "trial_history_complete": plan.evidence_audit.trial_history_complete,
        }
    if plan.role_calendar is not None:
        role_calendar_payload = {
            "development_sessions": [
                session.isoformat() for session in plan.role_calendar.development_sessions
            ],
            "warmup_sessions": [
                session.isoformat() for session in plan.role_calendar.warmup_sessions
            ],
            "evaluation_sessions": [
                session.isoformat() for session in plan.role_calendar.evaluation_sessions
            ],
        }
        if plan.role_calendar.quarantined_sessions:
            role_calendar_payload["quarantined_sessions"] = [
                session.isoformat() for session in plan.role_calendar.quarantined_sessions
            ]
        payload["role_calendar"] = role_calendar_payload
    if plan.study_identity is not None:
        payload["study_identity"] = {
            "study_path": plan.study_identity.study_path,
            "preregistration_sha256": plan.study_identity.preregistration_sha256,
            "plan_sha256": plan.study_identity.plan_sha256,
            "candidate_freeze_sha256": plan.study_identity.candidate_freeze_sha256,
            "qualification_spec_sha256": plan.study_identity.qualification_spec_sha256,
            "workflow_release_sha256": plan.study_identity.workflow_release_sha256,
        }
        if plan.study_identity.development_authorization_sha256 is not None:
            payload["study_identity"]["development_authorization_sha256"] = (
                plan.study_identity.development_authorization_sha256
            )
        if plan.study_identity.trial_registry_identity is not None:
            payload["study_identity"]["trial_registry_identity"] = (
                plan.study_identity.trial_registry_identity
            )
            payload["study_identity"]["qualification_registry_identity"] = (
                plan.study_identity.qualification_registry_identity
            )
        if plan.study_identity.policy_set_identity is not None:
            payload["study_identity"]["policy_set_identity"] = (
                plan.study_identity.policy_set_identity
            )
            payload["study_identity"]["evidence_contract_sha256"] = (
                plan.study_identity.evidence_contract_sha256
            )
        if plan.study_identity.operation_approved_by is not None:
            payload["study_identity"]["operation_approved_by"] = (
                plan.study_identity.operation_approved_by
            )
            payload["study_identity"]["operation_approved_at"] = timestamp_text(
                plan.study_identity.operation_approved_at
            )
            payload["study_identity"]["contamination_declaration"] = (
                plan.study_identity.contamination_declaration
            )
            payload["study_identity"]["trial_registry_path"] = (
                plan.study_identity.trial_registry_path
            )
            payload["study_identity"]["qualification_registry_path"] = (
                plan.study_identity.qualification_registry_path
            )
    return payload


def historical_plan_payload(plan: HistoricalQualificationPlan) -> dict[str, object]:
    """Return the canonical persisted payload for transaction coordination."""
    return _historical_plan_payload(plan)


def _historical_plan_from_payload(payload: Mapping[str, object]) -> HistoricalQualificationPlan:
    try:
        thresholds_payload = _mapping_field(payload, "thresholds")
        benchmark_payload = _mapping_field(payload, "benchmarks")
        adjustment_payload = _mapping_field(payload, "selection_adjustment")
        costs = _mapping_field(payload, "cost_policies")
        base_cost = _execution_cost_policy(_mapping_field(costs, "base"))
        stress_cost = _execution_cost_policy(_mapping_field(costs, "stress"))
        raw_folds = payload["folds"]
        raw_sessions = payload["evaluation_sessions"]
        raw_development_years = payload["development_years"]
        if not isinstance(raw_folds, list) or not isinstance(raw_sessions, list):
            raise ValueError("plan folds or sessions are malformed")
        if not isinstance(raw_development_years, list):
            raise ValueError("plan development years are malformed")
        folds = tuple(
            EvaluationFold(
                fold_id=str(item["fold_id"]),
                evaluation_year=int(item["evaluation_year"]),
                outcome_start=date.fromisoformat(str(item["outcome_start"])),
                outcome_end=date.fromisoformat(str(item["outcome_end"])),
                signal_start=date.fromisoformat(str(item["signal_start"])),
                signal_end=date.fromisoformat(str(item["signal_end"])),
            )
            for item in raw_folds
            if isinstance(item, Mapping)
        )
        if len(folds) != len(raw_folds):
            raise ValueError("plan folds are malformed")
        raw_epoch = payload.get("forward_selection_epoch")
        epoch = None
        if raw_epoch is not None:
            epoch_payload = _mapping_value(raw_epoch, "forward selection epoch")
            included = epoch_payload["included_trial_ids"]
            if not isinstance(included, list):
                raise ValueError("forward selection epoch trial identities are malformed")
            prior_incomplete = epoch_payload["prior_selection_history_incomplete"]
            if type(prior_incomplete) is not bool:
                raise ValueError("forward selection epoch history flag is malformed")
            epoch = ForwardSelectionEpoch(
                started_at=parse_timestamp(str(epoch_payload["started_at"])),
                selected_trial_id=str(epoch_payload["selected_trial_id"]),
                included_trial_ids=tuple(str(item) for item in included),
                prior_selection_history_incomplete=prior_incomplete,
            )
        raw_checkpoint = payload.get("retrospective_selection_checkpoint")
        retrospective_checkpoint = None
        if raw_checkpoint is not None:
            checkpoint_payload = _mapping_value(
                raw_checkpoint,
                "retrospective selection checkpoint",
            )
            included = checkpoint_payload["included_trial_ids"]
            if not isinstance(included, list):
                raise ValueError("retrospective trial identities are malformed")
            prior_incomplete = checkpoint_payload["prior_selection_history_incomplete"]
            if type(prior_incomplete) is not bool:
                raise ValueError("retrospective history flag is malformed")
            retrospective_checkpoint = RetrospectiveSelectionCheckpoint(
                frozen_at=parse_timestamp(str(checkpoint_payload["frozen_at"])),
                selected_trial_id=str(checkpoint_payload["selected_trial_id"]),
                included_trial_ids=tuple(str(item) for item in included),
                prior_selection_history_incomplete=prior_incomplete,
            )
        evidence_role = str(payload.get("evidence_role", "historical"))
        if evidence_role not in EVIDENCE_ROLES:
            raise ValueError("plan evidence role is malformed")
        raw_audit = payload.get("evidence_audit")
        audit = None
        if raw_audit is not None:
            audit_payload = _mapping_value(raw_audit, "clean-evidence audit")
            trial_history_complete = audit_payload["trial_history_complete"]
            if type(trial_history_complete) is not bool:
                raise ValueError("clean-evidence trial-history flag is malformed")
            audit = EvaluationEvidenceAudit(
                classification=str(audit_payload["classification"]),
                frozen_at=parse_timestamp(str(audit_payload["frozen_at"])),
                justification=str(audit_payload["justification"]),
                trial_history_complete=trial_history_complete,
            )
        raw_role_calendar = payload.get("role_calendar")
        role_calendar = None
        if raw_role_calendar is not None:
            calendar_payload = _mapping_value(raw_role_calendar, "qualification role calendar")
            raw_development_sessions = calendar_payload["development_sessions"]
            raw_warmup_sessions = calendar_payload["warmup_sessions"]
            raw_evaluation_sessions = calendar_payload["evaluation_sessions"]
            raw_quarantined_sessions = calendar_payload.get("quarantined_sessions", [])
            if not all(
                isinstance(items, list)
                for items in (
                    raw_development_sessions,
                    raw_warmup_sessions,
                    raw_evaluation_sessions,
                    raw_quarantined_sessions,
                )
            ):
                raise ValueError("qualification role calendar sessions are malformed")
            role_calendar = QualificationRoleCalendar(
                development_sessions=tuple(
                    date.fromisoformat(str(item)) for item in raw_development_sessions
                ),
                warmup_sessions=tuple(
                    date.fromisoformat(str(item)) for item in raw_warmup_sessions
                ),
                evaluation_sessions=tuple(
                    date.fromisoformat(str(item)) for item in raw_evaluation_sessions
                ),
                quarantined_sessions=tuple(
                    date.fromisoformat(str(item)) for item in raw_quarantined_sessions
                ),
            )
        raw_study_identity = payload.get("study_identity")
        study_identity = None
        if raw_study_identity is not None:
            identity_payload = _mapping_value(raw_study_identity, "study qualification identity")
            qualification_spec_sha256 = identity_payload.get("qualification_spec_sha256")
            if qualification_spec_sha256 is not None and not isinstance(
                qualification_spec_sha256, str
            ):
                raise ValueError("study qualification spec digest is malformed")
            development_authorization_sha256 = identity_payload.get(
                "development_authorization_sha256"
            )
            if development_authorization_sha256 is not None and not isinstance(
                development_authorization_sha256, str
            ):
                raise ValueError("Development authorization digest is malformed")
            study_identity = StudyQualificationIdentity(
                study_path=str(identity_payload["study_path"]),
                preregistration_sha256=str(identity_payload["preregistration_sha256"]),
                plan_sha256=str(identity_payload["plan_sha256"]),
                candidate_freeze_sha256=str(identity_payload["candidate_freeze_sha256"]),
                qualification_spec_sha256=qualification_spec_sha256,
                workflow_release_sha256=str(identity_payload["workflow_release_sha256"]),
                development_authorization_sha256=development_authorization_sha256,
                operation_approved_by=(
                    str(identity_payload["operation_approved_by"])
                    if identity_payload.get("operation_approved_by") is not None
                    else None
                ),
                operation_approved_at=(
                    parse_timestamp(str(identity_payload["operation_approved_at"]))
                    if identity_payload.get("operation_approved_at") is not None
                    else None
                ),
                contamination_declaration=(
                    str(identity_payload["contamination_declaration"])
                    if identity_payload.get("contamination_declaration") is not None
                    else None
                ),
                trial_registry_path=(
                    str(identity_payload["trial_registry_path"])
                    if identity_payload.get("trial_registry_path") is not None
                    else None
                ),
                qualification_registry_path=(
                    str(identity_payload["qualification_registry_path"])
                    if identity_payload.get("qualification_registry_path") is not None
                    else None
                ),
                trial_registry_identity=(
                    str(identity_payload["trial_registry_identity"])
                    if identity_payload.get("trial_registry_identity") is not None
                    else None
                ),
                qualification_registry_identity=(
                    str(identity_payload["qualification_registry_identity"])
                    if identity_payload.get("qualification_registry_identity") is not None
                    else None
                ),
                policy_set_identity=(
                    str(identity_payload["policy_set_identity"])
                    if identity_payload.get("policy_set_identity") is not None
                    else None
                ),
                evidence_contract_sha256=(
                    str(identity_payload["evidence_contract_sha256"])
                    if identity_payload.get("evidence_contract_sha256") is not None
                    else None
                ),
            )
        plan = HistoricalQualificationPlan(
            plan_id=str(payload["plan_id"]),
            experiment_family=str(payload["experiment_family"]),
            definition_fingerprint=str(payload["definition_fingerprint"]),
            created_at=parse_timestamp(str(payload["created_at"])),
            development_years=tuple(int(item) for item in raw_development_years),
            evaluation_sessions=tuple(date.fromisoformat(str(item)) for item in raw_sessions),
            folds=folds,
            maximum_holding_sessions=int(payload["maximum_holding_sessions"]),
            execution_lag_sessions=int(payload["execution_lag_sessions"]),
            dependency_sessions=int(payload["dependency_sessions"]),
            embargo_sessions=int(payload["embargo_sessions"]),
            stress_drawdown_limit=Decimal(str(payload["stress_drawdown_limit"])),
            base_cost_policy=base_cost,
            stress_cost_policy=stress_cost,
            thresholds=HistoricalScreenThresholds(
                minimum_development_years=int(thresholds_payload["minimum_development_years"]),
                minimum_evaluation_folds=int(thresholds_payload["minimum_evaluation_folds"]),
                minimum_completed_trades=int(thresholds_payload["minimum_completed_trades"]),
                minimum_traded_folds=int(thresholds_payload["minimum_traded_folds"]),
                minimum_positive_fold_rate=Decimal(
                    str(thresholds_payload["minimum_positive_fold_rate"])
                ),
                minimum_cumulative_return=Decimal(
                    str(thresholds_payload["minimum_cumulative_return"])
                ),
                minimum_profit_factor=Decimal(str(thresholds_payload["minimum_profit_factor"])),
                minimum_stress_cumulative_return=Decimal(
                    str(thresholds_payload["minimum_stress_cumulative_return"])
                ),
                minimum_stress_profit_factor=Decimal(
                    str(thresholds_payload["minimum_stress_profit_factor"])
                ),
                maximum_fold_concentration=Decimal(
                    str(thresholds_payload["maximum_fold_concentration"])
                ),
                selection_confidence=Decimal(str(thresholds_payload["selection_confidence"])),
            ),
            benchmarks=HistoricalBenchmarkPolicy(
                family_baseline_trial_id=str(benchmark_payload["family_baseline_trial_id"]),
                random_seed=int(benchmark_payload["random_seed"]),
                random_samples=int(benchmark_payload["random_samples"]),
            ),
            selection_adjustment=SelectionAdjustmentPolicy(
                repetitions=int(adjustment_payload["repetitions"]),
                block_sessions=int(adjustment_payload["block_sessions"]),
            ),
            forward_selection_epoch=epoch,
            retrospective_selection_checkpoint=retrospective_checkpoint,
            evidence_role=evidence_role,
            evidence_audit=audit,
            role_calendar=role_calendar,
            study_identity=study_identity,
        )
        _validate_plan_selection_boundaries(plan)
        _validate_plan_role_calendar(plan)
        return plan
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise QualificationRegistryError(f"historical plan payload is malformed: {exc}") from exc


def historical_plan_from_payload(
    payload: Mapping[str, object],
) -> HistoricalQualificationPlan:
    """Rehydrate one canonical plan payload for transaction recovery."""
    return _historical_plan_from_payload(payload)


def _historical_screen_from_payload(
    payload: Mapping[str, object],
) -> HistoricalScreenResult:
    raw_folds = payload.get("folds")
    if not isinstance(raw_folds, list) or not raw_folds:
        raise QualificationRegistryError("historical screen folds are malformed")
    aggregate = _mapping_value(payload.get("aggregate"), "historical screen aggregate")
    benchmarks = _mapping_value(payload.get("benchmarks"), "historical screen benchmarks")
    selection = _mapping_value(
        payload.get("selection_adjustment"),
        "historical screen selection adjustment",
    )
    raw_samples = benchmarks.get("random_entry_samples")
    raw_gates = payload.get("gates")
    if not isinstance(raw_samples, list) or not isinstance(raw_gates, list):
        raise QualificationRegistryError("historical screen benchmarks or gates are malformed")
    try:
        return HistoricalScreenResult(
            plan_id=_required_string(payload.get("plan_id"), "historical screen plan"),
            folds=tuple(
                HistoricalFoldEvidence(
                    fold_id=_required_string(item.get("fold_id"), "historical fold"),
                    evaluation_year=_strict_int(item.get("evaluation_year")),
                    signal_count=_strict_int(item.get("signal_count")),
                    candidate_count=_strict_int(item.get("candidate_count")),
                    completed_trades=_strict_int(item.get("completed_trades")),
                    cumulative_return=_finite_float(item.get("cumulative_return")),
                    stress_cumulative_return=_finite_float(item.get("stress_cumulative_return")),
                    stress_max_drawdown=_finite_float(item.get("stress_max_drawdown")),
                    gross_profit=_finite_float(item.get("gross_profit")),
                    gross_loss=_finite_float(item.get("gross_loss")),
                    stress_gross_profit=_finite_float(item.get("stress_gross_profit")),
                    stress_gross_loss=_finite_float(item.get("stress_gross_loss")),
                )
                for item in _mapping_list(raw_folds, "historical screen folds")
            ),
            aggregate=HistoricalAggregateEvidence(
                completed_trades=_strict_int(aggregate.get("completed_trades")),
                traded_folds=_strict_int(aggregate.get("traded_folds")),
                positive_traded_fold_rate=_finite_float(aggregate.get("positive_traded_fold_rate")),
                cumulative_return=_finite_float(aggregate.get("cumulative_return")),
                profit_factor=_required_string(
                    aggregate.get("profit_factor"), "aggregate profit factor"
                ),
                stress_cumulative_return=_finite_float(aggregate.get("stress_cumulative_return")),
                stress_profit_factor=_required_string(
                    aggregate.get("stress_profit_factor"), "stress profit factor"
                ),
                stress_max_drawdown=_finite_float(aggregate.get("stress_max_drawdown")),
                trade_fold_concentration=_finite_float(aggregate.get("trade_fold_concentration")),
                profit_fold_concentration=_finite_float(aggregate.get("profit_fold_concentration")),
            ),
            benchmarks=HistoricalBenchmarkEvidence(
                cash_return=_finite_float(benchmarks.get("cash_return")),
                family_baseline_return=_finite_float(benchmarks.get("family_baseline_return")),
                random_entry_samples=tuple(
                    ExposureMatchedRandomSample(
                        sample_index=_strict_int(item.get("sample_index")),
                        cumulative_return=_finite_float(item.get("cumulative_return")),
                        completed_trades=_strict_int(item.get("completed_trades")),
                        entry_months=_int_tuple(item.get("entry_months")),
                        holding_sessions=_int_tuple(item.get("holding_sessions")),
                    )
                    for item in _mapping_list(
                        raw_samples,
                        "historical screen random-entry samples",
                    )
                ),
            ),
            selection_adjustment=SelectionAdjustmentResult(
                selected_trial_id=_required_string(
                    selection.get("selected_trial_id"), "selected trial"
                ),
                included_trial_ids=_string_tuple(selection.get("included_trial_ids")),
                observed_mean_excess_return=Decimal(
                    _required_string(
                        selection.get("observed_mean_excess_return"),
                        "observed mean excess return",
                    )
                ),
                adjusted_confidence=Decimal(
                    _required_string(
                        selection.get("adjusted_confidence"),
                        "adjusted confidence",
                    )
                ),
                repetitions=_strict_int(selection.get("repetitions")),
                block_sessions=_strict_int(selection.get("block_sessions")),
                passed=_strict_bool(selection.get("passed")),
            ),
            gates=tuple(
                QualificationGate(
                    name=_required_string(item.get("name"), "historical gate"),
                    passed=_strict_bool(item.get("passed")),
                    actual=_required_string(item.get("actual"), "historical gate actual"),
                    threshold=_required_string(item.get("threshold"), "historical gate threshold"),
                )
                for item in _mapping_list(raw_gates, "historical screen gates")
            ),
            passed=_strict_bool(payload.get("passed")),
            disposition=_required_string(
                payload.get("disposition"), "historical screen disposition"
            ),
        )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise QualificationRegistryError(f"historical screen payload is malformed: {exc}") from exc


def _validate_plan_selection_boundaries(plan: HistoricalQualificationPlan) -> None:
    if plan.study_identity is not None:
        try:
            validate_study_qualification_identity(plan.study_identity)
        except ValueError as exc:
            raise QualificationRegistryError(str(exc)) from exc
    if (
        plan.forward_selection_epoch is not None
        and plan.retrospective_selection_checkpoint is not None
    ):
        raise QualificationRegistryError(
            "qualification plan cannot contain two selection boundaries"
        )
    if plan.evidence_role in RETROSPECTIVE_EVIDENCE_ROLES:
        if plan.retrospective_selection_checkpoint is None:
            raise QualificationRegistryError("retrospective plan requires frozen trial universe")
        if plan.forward_selection_epoch is not None:
            raise QualificationRegistryError(
                "retrospective qualification cannot claim a Forward Selection Epoch"
            )
    elif plan.retrospective_selection_checkpoint is not None:
        raise QualificationRegistryError(
            "Historical Evaluation cannot use a retrospective checkpoint"
        )


def _mapping_value(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _mapping_list(value: object, name: str) -> list[Mapping[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"{name} must be a list of objects")
    return value


def _strict_int(value: object) -> int:
    if type(value) is not int:
        raise ValueError("historical screen integer field is malformed")
    return value


def _strict_bool(value: object) -> bool:
    if type(value) is not bool:
        raise ValueError("historical screen boolean field is malformed")
    return value


def _finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("historical screen numeric field is malformed")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("historical screen numeric field is not finite")
    return parsed


def _required_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _int_tuple(value: object) -> tuple[int, ...]:
    if not isinstance(value, list) or not all(type(item) is int for item in value):
        raise ValueError("historical screen integer inventory is malformed")
    return tuple(value)


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError("historical screen identity inventory is malformed")
    return tuple(value)


def _mapping_field(payload: Mapping[str, object], name: str) -> Mapping[str, object]:
    return _mapping_value(payload[name], name)


def _execution_cost_policy(payload: Mapping[str, object]) -> ExecutionCostPolicy:
    return ExecutionCostPolicy(
        entry_slippage_bps=float(payload["entry_slippage_bps"]),
        exit_slippage_bps=float(payload["exit_slippage_bps"]),
        fee_bps_per_side=float(payload["fee_bps_per_side"]),
    )


def _historical_screen_payload(
    screen: HistoricalScreenResult,
    evaluated_at: datetime,
) -> dict[str, object]:
    aggregate = screen.aggregate
    selection = screen.selection_adjustment
    return {
        "plan_id": screen.plan_id,
        "evaluated_at": timestamp_text(evaluated_at),
        "folds": [
            {
                "fold_id": fold.fold_id,
                "evaluation_year": fold.evaluation_year,
                "signal_count": fold.signal_count,
                "candidate_count": fold.candidate_count,
                "completed_trades": fold.completed_trades,
                "cumulative_return": fold.cumulative_return,
                "stress_cumulative_return": fold.stress_cumulative_return,
                "stress_max_drawdown": fold.stress_max_drawdown,
                "gross_profit": fold.gross_profit,
                "gross_loss": fold.gross_loss,
                "stress_gross_profit": fold.stress_gross_profit,
                "stress_gross_loss": fold.stress_gross_loss,
            }
            for fold in screen.folds
        ],
        "aggregate": {
            "completed_trades": aggregate.completed_trades,
            "traded_folds": aggregate.traded_folds,
            "positive_traded_fold_rate": aggregate.positive_traded_fold_rate,
            "cumulative_return": aggregate.cumulative_return,
            "profit_factor": aggregate.profit_factor,
            "stress_cumulative_return": aggregate.stress_cumulative_return,
            "stress_profit_factor": aggregate.stress_profit_factor,
            "stress_max_drawdown": aggregate.stress_max_drawdown,
            "trade_fold_concentration": aggregate.trade_fold_concentration,
            "profit_fold_concentration": aggregate.profit_fold_concentration,
        },
        "benchmarks": {
            "cash_return": screen.benchmarks.cash_return,
            "family_baseline_return": screen.benchmarks.family_baseline_return,
            "random_entry_samples": [
                {
                    "sample_index": sample.sample_index,
                    "cumulative_return": sample.cumulative_return,
                    "completed_trades": sample.completed_trades,
                    "entry_months": list(sample.entry_months),
                    "holding_sessions": list(sample.holding_sessions),
                }
                for sample in screen.benchmarks.random_entry_samples
            ],
        },
        "selection_adjustment": {
            "selected_trial_id": selection.selected_trial_id,
            "included_trial_ids": list(selection.included_trial_ids),
            "observed_mean_excess_return": decimal_text(selection.observed_mean_excess_return),
            "adjusted_confidence": decimal_text(selection.adjusted_confidence),
            "repetitions": selection.repetitions,
            "block_sessions": selection.block_sessions,
            "passed": selection.passed,
        },
        "gates": [
            {
                "name": gate.name,
                "passed": gate.passed,
                "actual": gate.actual,
                "threshold": gate.threshold,
            }
            for gate in screen.gates
        ],
        "passed": screen.passed,
        "disposition": screen.disposition,
    }


def _registration_payload(
    registration: ShadowRegistration,
    *,
    recorded_at: datetime,
) -> dict[str, object]:
    policy = registration.activation_policy
    return {
        "shadow_id": registration.shadow_id,
        "trial_id": registration.trial_id,
        "historical_plan_id": registration.historical_plan_id,
        "experiment_family": registration.experiment_family,
        "definition_fingerprint": registration.definition_fingerprint,
        "definition_snapshot_id": registration.definition_snapshot_id,
        "definition_snapshot_byte_count": registration.definition_snapshot_byte_count,
        "prospective_start": timestamp_text(registration.prospective_start),
        "recorded_at": timestamp_text(recorded_at),
        "activation_checkpoint": registration.activation_checkpoint.isoformat(),
        "prior_shadow_id": registration.prior_shadow_id,
        "status": registration.status,
        "cost_policies": _cost_policy_payload(
            registration.base_cost_policy,
            registration.stress_cost_policy,
        ),
        "activation_policy": {
            "minimum_completed_sessions": policy.minimum_completed_sessions,
            "minimum_completed_trades": policy.minimum_completed_trades,
            "minimum_cumulative_return": decimal_text(policy.minimum_cumulative_return),
            "minimum_profit_factor": decimal_text(policy.minimum_profit_factor),
            "minimum_stress_cumulative_return": decimal_text(
                policy.minimum_stress_cumulative_return
            ),
            "minimum_stress_profit_factor": decimal_text(policy.minimum_stress_profit_factor),
            "stress_drawdown_limit": decimal_text(policy.stress_drawdown_limit),
        },
    }


def _evidence_payload(evidence: ShadowEvidence) -> dict[str, object]:
    return {
        "shadow_id": evidence.shadow_id,
        "definition_fingerprint": evidence.definition_fingerprint,
        "as_of": evidence.as_of.isoformat(),
        "data_cutoff": evidence.data_cutoff.isoformat(),
        "completed_sessions": evidence.completed_sessions,
        "paper_proposals": [
            {
                "proposal_id": proposal.proposal_id,
                "signal_date": proposal.signal_date.isoformat(),
                "entry_date": proposal.entry_date.isoformat(),
                "action": proposal.action,
            }
            for proposal in evidence.paper_proposals
        ],
        "simulated_fills": [
            {
                "proposal_id": fill.proposal_id,
                "quantity": fill.quantity,
                "executed_entry_price": fill.executed_entry_price,
                "executed_exit_price": fill.executed_exit_price,
                "pnl": fill.pnl,
            }
            for fill in evidence.simulated_fills
        ],
        "cumulative_return": evidence.cumulative_return,
        "profit_factor": evidence.profit_factor,
        "stress_cumulative_return": evidence.stress_cumulative_return,
        "stress_profit_factor": evidence.stress_profit_factor,
        "stress_max_drawdown": evidence.stress_max_drawdown,
        "critical_drift": evidence.critical_drift,
    }


def _activation_payload(
    evaluation: ShadowActivationEvaluation,
    evaluated_at: date,
) -> dict[str, object]:
    return {
        "shadow_id": evaluation.shadow_id,
        "evaluated_at": evaluated_at.isoformat(),
        "gates": [
            {
                "name": gate.name,
                "passed": gate.passed,
                "actual": gate.actual,
                "threshold": gate.threshold,
            }
            for gate in evaluation.gates
        ],
        "eligible": evaluation.eligible,
        "disposition": evaluation.disposition,
        "authorized_for_live_orders": evaluation.authorized_for_live_orders,
    }


def _cost_policy_payload(
    base: ExecutionCostPolicy,
    stress: ExecutionCostPolicy,
) -> dict[str, object]:
    return {
        "base": {
            "entry_slippage_bps": base.entry_slippage_bps,
            "exit_slippage_bps": base.exit_slippage_bps,
            "fee_bps_per_side": base.fee_bps_per_side,
        },
        "stress": {
            "entry_slippage_bps": stress.entry_slippage_bps,
            "exit_slippage_bps": stress.exit_slippage_bps,
            "fee_bps_per_side": stress.fee_bps_per_side,
        },
    }

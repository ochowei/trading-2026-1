"""Exact evidence linkage for study-time retrospective terminal decisions."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from trading.core.accounting import canonical_json_bytes
from trading.research_data import QualificationEvidenceStore
from trading.research_data.artifacts import ImmutableBlobCorruptionError
from trading.research_data.paths import ResultPathMigrationError, resolve_result_path
from trading.workflow.study_qualification import (
    FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    REQUIRED_STUDY_TIME_CHALLENGES,
)

TERMINAL_EVIDENCE_FILENAME = "TERMINAL_EVIDENCE.json"


def validate_study_time_terminal_evidence(
    *,
    study_path: Path,
    outcome: str,
    disposition: str | None,
    decision_stage: str,
    require_current_registry: bool = False,
) -> str:
    """Verify the terminal decision against linked frozen registry and gate artifacts."""
    study = Path(study_path).resolve()
    terminal_path = study / TERMINAL_EVIDENCE_FILENAME
    terminal = _json_object(terminal_path)
    if terminal.get("schema_version") != 1:
        raise ValueError("TERMINAL_EVIDENCE.json schema_version must be 1")
    relative_study = study.relative_to(study.parents[4]).as_posix()
    spec = _json_object(study / "QUALIFICATION_SPEC.json")
    route = spec.get("route", terminal.get("route"))
    if route not in {"study-time-retrospective", FIXED_CALENDAR_RETROSPECTIVE_ROUTE}:
        raise ValueError("terminal evidence requires a supported retrospective study route")
    expected = {
        "study_path": relative_study,
        "route": route,
        "decision_stage": decision_stage,
        "preregistration_sha256": _sha256(study / "PREREGISTRATION.json"),
        "qualification_spec_sha256": _sha256(study / "QUALIFICATION_SPEC.json"),
        "development_authorization_sha256": _sha256(study / "DEVELOPMENT_AUTHORIZATION.json"),
    }
    for field, value in expected.items():
        if terminal.get(field) != value:
            raise ValueError(f"terminal evidence {field} differs from the frozen study")

    if outcome == "indeterminate":
        if disposition is not None or not str(terminal.get("integrity_issue") or "").strip():
            raise ValueError("indeterminate terminal evidence needs an integrity issue only")
        return _sha256(terminal_path)
    if outcome == "fail" and decision_stage == "development":
        if disposition != "development-selection-failed":
            raise ValueError("Development failure disposition is inconsistent")
        if (study / "CANDIDATE_FREEZE.json").exists():
            raise ValueError("Development failure cannot follow an existing candidate freeze")
        if "qualification_evidence" in terminal or "candidate_freeze_sha256" in terminal:
            raise ValueError("Development failure must precede candidate freeze and qualification")
        _validate_development_failure(
            study,
            terminal,
            require_current_registry=require_current_registry,
        )
        return _sha256(terminal_path)

    allowed_stages = (
        {"fixed-historical-evaluation", "retrospective-execution-replay"}
        if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
        else {"retrospective-evaluation"}
    )
    if decision_stage not in allowed_stages:
        raise ValueError("retrospective pass/fail uses an invalid decision stage")
    candidate_freeze = study / "CANDIDATE_FREEZE.json"
    if terminal.get("candidate_freeze_sha256") != _sha256(candidate_freeze):
        raise ValueError("terminal evidence differs from the candidate freeze")
    screen_passed = _validate_registry_link(study, terminal)
    challenges_passed = _validate_challenge_manifest(study, terminal)
    replay_passed: bool | None = None
    if (
        route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
        and decision_stage == "retrospective-execution-replay"
    ):
        replay_passed = _validate_fixed_replay(study, terminal)
    if outcome == "pass":
        if (
            disposition != "retrospectively-supported"
            or not (screen_passed and challenges_passed)
            or (route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE and replay_passed is not True)
        ):
            raise ValueError("pass requires a linked passing screen and every challenge gate")
    elif outcome == "fail":
        if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE:
            valid_failure = (
                decision_stage == "fixed-historical-evaluation"
                and disposition == "fixed-evaluation-failed"
                and not (screen_passed and challenges_passed)
            ) or (
                decision_stage == "retrospective-execution-replay"
                and disposition == "retrospective-replay-failed"
                and screen_passed
                and challenges_passed
                and replay_passed is False
            )
            if not valid_failure:
                raise ValueError("fixed-calendar fail requires a failed gate at its exact stage")
        elif disposition != "retrospective-screen-failed" or (screen_passed and challenges_passed):
            raise ValueError("retrospective fail requires at least one linked failed gate")
    else:
        raise ValueError("fixed study-time evidence cannot support insufficient-evidence")
    return _sha256(terminal_path)


def _validate_fixed_replay(study: Path, terminal: dict[str, Any]) -> bool:
    from trading.workflow.retrospective_replay import validate_retrospective_replay_artifact

    reference = _mapping(terminal.get("retrospective_replay"), "retrospective replay")
    path = _study_evidence_reference(study, reference.get("path"))
    if reference.get("sha256") != _sha256(path):
        raise ValueError("retrospective replay digest differs from terminal evidence")
    payload = _json_object(path)
    qualification = _mapping(terminal.get("qualification_evidence"), "qualification evidence")
    if payload.get("qualification_plan_id") != qualification.get("plan_id"):
        raise ValueError("retrospective replay uses a different qualification plan")
    return validate_retrospective_replay_artifact(study, path)


def _validate_development_failure(
    study: Path,
    terminal: dict[str, Any],
    *,
    require_current_registry: bool,
) -> None:
    reference = _mapping(terminal.get("development_gate"), "development gate")
    path = _study_evidence_reference(study, reference.get("path"))
    if reference.get("sha256") != _sha256(path):
        raise ValueError("Development gate digest differs from terminal evidence")
    gate = _json_object(path)
    required = {
        "study_path": terminal["study_path"],
        "preregistration_sha256": terminal["preregistration_sha256"],
        "qualification_spec_sha256": terminal["qualification_spec_sha256"],
        "development_authorization_sha256": terminal["development_authorization_sha256"],
        "complete": True,
        "trustworthy": True,
        "eligible_candidate": None,
        "disposition": "development-selection-failed",
    }
    if any(gate.get(field) != value for field, value in required.items()):
        raise ValueError("Development failure gate is incomplete or belongs to another study")
    if type(gate.get("trial_budget_exhausted")) is not bool:
        raise ValueError("Development failure gate needs a typed budget disposition")
    snapshot = _resolve_qualification_snapshot(
        study,
        terminal,
        field="qualification_absence_evidence",
        label="qualification absence evidence",
    )
    _trial_registry_identity, expected_identity = _frozen_registry_identities(study)
    if snapshot.source_registry_identity != expected_identity:
        raise ValueError("qualification absence evidence uses a different frozen registry")
    if require_current_registry:
        root = study.parents[4]
        current = root / expected_identity
        checkpoint = current.with_name(f".{current.name}.head.json")
        if not current.is_file() or not checkpoint.is_file():
            raise ValueError("current frozen qualification registry is unavailable")
        if (
            _sha256(current) != snapshot.registry_sha256
            or _sha256(checkpoint) != snapshot.checkpoint_sha256
        ):
            raise ValueError("qualification absence evidence is not the current registry head")
    matching_plans = []
    for event in _registry_events(snapshot.state):
        if event.get("event_type") != "historical_plan":
            continue
        payload = _mapping(event.get("payload"), "qualification plan")
        identity = payload.get("study_identity")
        if isinstance(identity, dict) and identity.get("study_path") == terminal["study_path"]:
            matching_plans.append(payload.get("plan_id"))
    if matching_plans:
        raise ValueError("Development failure cannot follow a qualification plan or screen")


def _validate_registry_link(study: Path, terminal: dict[str, Any]) -> bool:
    reference = _mapping(terminal.get("qualification_evidence"), "qualification evidence")
    snapshot = _resolve_qualification_snapshot(
        study,
        terminal,
        field="qualification_evidence",
        label="qualification evidence",
    )
    trial_registry_identity, qualification_registry_identity = _frozen_registry_identities(study)
    if snapshot.source_registry_identity != qualification_registry_identity:
        raise ValueError("qualification evidence uses a different frozen registry")
    events = _registry_events(snapshot.state)
    plan_id = reference.get("plan_id")
    screen_event_id = reference.get("screen_event_id")
    if not isinstance(plan_id, str) or screen_event_id != f"historical-screen:{plan_id}":
        raise ValueError("terminal evidence must link the canonical historical screen")
    plan = next(
        (
            item
            for item in events
            if item.get("event_type") == "historical_plan"
            and isinstance(item.get("payload"), dict)
            and item["payload"].get("plan_id") == plan_id
        ),
        None,
    )
    screen = next((item for item in events if item.get("event_id") == screen_event_id), None)
    if plan is None or screen is None or screen.get("event_type") != "historical_screen":
        raise ValueError("terminal evidence has no exact linked plan and screen")
    plan_payload = _mapping(plan.get("payload"), "qualification plan")
    screen_payload = _mapping(screen.get("payload"), "qualification screen")
    identity = _mapping(plan_payload.get("study_identity"), "plan study identity")
    qualification_spec = _json_object(study / "QUALIFICATION_SPEC.json")
    frozen_policy_set = _mapping(qualification_spec.get("policy_set"), "policy set")
    frozen_evidence_contract = _mapping(
        qualification_spec.get("evidence_contract"), "evidence contract"
    )
    expected_identity = {
        "study_path": terminal["study_path"],
        "preregistration_sha256": terminal["preregistration_sha256"],
        "plan_sha256": _sha256(study / "PLAN.md"),
        "candidate_freeze_sha256": terminal["candidate_freeze_sha256"],
        "qualification_spec_sha256": terminal["qualification_spec_sha256"],
        "development_authorization_sha256": terminal["development_authorization_sha256"],
        "workflow_release_sha256": _sha256(study.parents[2] / "RELEASE.json"),
        "policy_set_identity": frozen_policy_set.get("identity"),
        "evidence_contract_sha256": hashlib.sha256(
            canonical_json_bytes(frozen_evidence_contract)
        ).hexdigest(),
    }
    if any(identity.get(field) != value for field, value in expected_identity.items()):
        raise ValueError("qualification plan belongs to a different frozen study")
    if (
        identity.get("trial_registry_identity") != trial_registry_identity
        or identity.get("qualification_registry_identity") != qualification_registry_identity
    ):
        raise ValueError("qualification plan uses different frozen registry identities")
    if (
        not str(identity.get("operation_approved_by") or "").strip()
        or not str(identity.get("operation_approved_at") or "").strip()
        or not str(identity.get("contamination_declaration") or "").strip()
    ):
        raise ValueError("qualification plan lacks durable study-time human authorization")
    if (
        plan_payload.get("evidence_role")
        not in {"study-time-retrospective", FIXED_CALENDAR_RETROSPECTIVE_ROUTE}
        or screen_payload.get("plan_id") != plan_id
        or type(screen_payload.get("passed")) is not bool
    ):
        raise ValueError("qualification screen is incomplete or has the wrong evidence role")
    expected_disposition = (
        "retrospectively-supported" if screen_payload["passed"] else "retrospective-screen-failed"
    )
    if screen_payload.get("disposition") != expected_disposition:
        raise ValueError("qualification screen disposition conflicts with its gates")
    gates = screen_payload.get("gates")
    if (
        not isinstance(gates, list)
        or not gates
        or not all(isinstance(item, dict) for item in gates)
    ):
        raise ValueError("qualification screen gates are missing")
    if screen_payload["passed"] != all(item.get("passed") is True for item in gates):
        raise ValueError("qualification screen pass state conflicts with its complete gates")
    return bool(screen_payload["passed"])


def _resolve_qualification_snapshot(
    study: Path,
    terminal: dict[str, Any],
    *,
    field: str,
    label: str,
):
    reference = _mapping(terminal.get(field), label)
    digest = reference.get("sha256")
    if not isinstance(digest, str):
        raise ValueError("qualification evidence digest is missing")
    root = study.parents[4].resolve()
    identity = reference.get("path")
    if not isinstance(identity, str):
        raise ValueError("qualification evidence path is missing")
    relative = Path(identity)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != identity:
        raise ValueError("qualification evidence path is unsafe")
    historical_namespace = relative.parts[:2] == ("results", "qualification-evidence")
    canonical_namespace = relative.parts[:3] == (
        "results",
        "evidence",
        "qualification",
    )
    if not (historical_namespace or canonical_namespace):
        raise ValueError("qualification evidence path is not canonical")
    try:
        expected_path = resolve_result_path(root / relative, repository_root=root)
    except ResultPathMigrationError as exc:
        raise ValueError(str(exc)) from exc
    if expected_path.name != f"{digest}.json":
        raise ValueError("qualification evidence path differs from its digest")
    store = QualificationEvidenceStore(expected_path.parent)
    try:
        return store.resolve(digest)
    except ImmutableBlobCorruptionError as exc:
        raise ValueError(str(exc)) from exc


def _registry_events(registry: dict[str, object]) -> list[dict[str, Any]]:
    events = registry.get("events")
    if not isinstance(events, list) or not all(isinstance(item, dict) for item in events):
        raise ValueError("qualification registry events are malformed")
    return events


def _frozen_registry_identities(study: Path) -> tuple[str, str]:
    spec = _json_object(study / "QUALIFICATION_SPEC.json")
    registries = _mapping(spec.get("registries"), "qualification spec registries")
    identities = (
        registries.get("trial_registry_path"),
        registries.get("qualification_registry_path"),
    )
    if any(not isinstance(identity, str) or not identity.strip() for identity in identities):
        raise ValueError("qualification spec has no frozen registry identity")
    typed = tuple(str(identity) for identity in identities)
    if any(
        (path := Path(identity)).is_absolute() or ".." in path.parts or path.as_posix() != identity
        for identity in typed
    ):
        raise ValueError("qualification spec registry identity is unsafe")
    return typed[0], typed[1]


def _validate_challenge_manifest(study: Path, terminal: dict[str, Any]) -> bool:
    reference = _mapping(terminal.get("challenge_manifest"), "challenge manifest")
    path = _study_evidence_reference(study, reference.get("path"))
    if reference.get("sha256") != _sha256(path):
        raise ValueError("challenge manifest digest differs from terminal evidence")
    manifest = _json_object(path)
    expected = {
        "study_path": terminal["study_path"],
        "preregistration_sha256": terminal["preregistration_sha256"],
        "candidate_freeze_sha256": terminal["candidate_freeze_sha256"],
        "qualification_spec_sha256": terminal["qualification_spec_sha256"],
        "development_authorization_sha256": terminal["development_authorization_sha256"],
        "qualification_plan_id": _mapping(
            terminal["qualification_evidence"], "qualification evidence"
        )["plan_id"],
    }
    if any(manifest.get(field) != value for field, value in expected.items()):
        raise ValueError("challenge manifest belongs to a different frozen study or plan")
    gates = manifest.get("gates")
    if not isinstance(gates, list) or not all(isinstance(item, dict) for item in gates):
        raise ValueError("challenge manifest gates are malformed")
    gate_ids = [str(item.get("id")) for item in gates]
    if (
        len(gate_ids) != len(REQUIRED_STUDY_TIME_CHALLENGES)
        or len(set(gate_ids)) != len(gate_ids)
        or set(gate_ids) != REQUIRED_STUDY_TIME_CHALLENGES
    ):
        raise ValueError("challenge manifest is missing a required challenge")
    spec = _json_object(study / "QUALIFICATION_SPEC.json")
    frozen_challenges = spec.get("required_challenges")
    if not isinstance(frozen_challenges, list) or not all(
        isinstance(item, dict) for item in frozen_challenges
    ):
        raise ValueError("frozen challenge gates are malformed")
    frozen = {str(item.get("id")): item for item in frozen_challenges}
    evidence_paths: set[Path] = set()
    for gate in gates:
        if type(gate.get("passed")) is not bool:
            raise ValueError("challenge gate pass state must be boolean")
        frozen_challenge = frozen.get(str(gate.get("id")), {})
        if gate.get("gate") != frozen_challenge.get("gate"):
            raise ValueError(f"challenge gate differs from preregistration: {gate.get('id')}")
        if gate.get("evidence_identity") != frozen_challenge.get("evidence_identity") or gate.get(
            "applies_to"
        ) != frozen_challenge.get("applies_to"):
            raise ValueError(f"challenge identity differs from preregistration: {gate.get('id')}")
        evidence = _mapping(gate.get("evidence"), "challenge evidence")
        evidence_path = _study_evidence_reference(study, evidence.get("path"))
        if evidence_path in evidence_paths:
            raise ValueError("required challenges must use distinct immutable evidence artifacts")
        evidence_paths.add(evidence_path)
        if evidence.get("sha256") != _sha256(evidence_path):
            raise ValueError(f"challenge evidence digest differs: {gate.get('id')}")
        artifact = _json_object(evidence_path)
        artifact_expected = {
            "schema_version": 1,
            "study_path": terminal["study_path"],
            "qualification_spec_sha256": terminal["qualification_spec_sha256"],
            "candidate_freeze_sha256": terminal["candidate_freeze_sha256"],
            "qualification_plan_id": expected["qualification_plan_id"],
            "challenge_id": gate.get("id"),
            "evidence_identity": frozen_challenge.get("evidence_identity"),
            "applies_to": frozen_challenge.get("applies_to"),
            "metric": _mapping(frozen_challenge.get("gate"), "frozen gate").get("metric"),
        }
        if any(artifact.get(field) != value for field, value in artifact_expected.items()):
            raise ValueError(f"challenge evidence schema/identity differs: {gate.get('id')}")
        if artifact.get("observed") is None or not _observed_equal(
            gate.get("observed"), artifact["observed"]
        ):
            raise ValueError(f"challenge manifest observed value lacks evidence: {gate.get('id')}")
        computed = _evaluate_typed_gate(
            artifact["observed"],
            _mapping(gate["gate"], "gate"),
        )
        if gate["passed"] != computed:
            raise ValueError(f"challenge gate pass state is not reproducible: {gate.get('id')}")
    return all(gate["passed"] for gate in gates)


def _repo_reference(study: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("terminal evidence path is missing")
    root = study.parents[4]
    requested = (root / value).resolve()
    try:
        requested.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("terminal evidence path escapes the repository") from exc
    try:
        return resolve_result_path(requested, repository_root=root)
    except ResultPathMigrationError as exc:
        raise ValueError(str(exc)) from exc


def _study_evidence_reference(study: Path, value: object) -> Path:
    """Resolve one tracked canonical Development/challenge evidence artifact."""
    if not isinstance(value, str):
        raise ValueError("terminal evidence path is missing")
    relative = Path(value)
    allowed = relative.parts[:2] == ("results", "study-evidence") or relative.parts[:2] == (
        "results",
        "workflows",
    )
    if not allowed:
        raise ValueError("Development and challenge evidence uses an invalid result namespace")
    resolved = _repo_reference(study, value)
    return resolved


def _json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read terminal evidence {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"terminal evidence must be an object: {path}")
    return payload


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"terminal evidence {name} is malformed")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evaluate_typed_gate(observed: object, gate: dict[str, Any]) -> bool:
    operator = gate.get("operator")
    threshold = gate.get("threshold")
    if operator in {"=", "==", "!="}:
        equal = observed == threshold
        if not equal and not isinstance(observed, bool) and not isinstance(threshold, bool):
            try:
                equal = Decimal(str(observed)) == Decimal(str(threshold))
            except InvalidOperation:
                equal = str(observed) == str(threshold)
        return not equal if operator == "!=" else equal
    if operator not in {">", ">=", "<", "<="}:
        raise ValueError(f"unsupported challenge gate operator: {operator}")
    try:
        actual_number = Decimal(str(observed))
        threshold_number = Decimal(str(threshold))
    except InvalidOperation as exc:
        raise ValueError("ordered challenge gate values must be numeric") from exc
    if operator == ">":
        return actual_number > threshold_number
    if operator == ">=":
        return actual_number >= threshold_number
    if operator == "<":
        return actual_number < threshold_number
    return actual_number <= threshold_number


def _observed_equal(manifest_value: object, evidence_value: object) -> bool:
    if manifest_value == evidence_value:
        return True
    if isinstance(manifest_value, bool) or isinstance(evidence_value, bool):
        return False
    try:
        return Decimal(str(manifest_value)) == Decimal(str(evidence_value))
    except InvalidOperation:
        return False

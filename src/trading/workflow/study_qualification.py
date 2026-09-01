"""Fail-closed compilation of qualification plans from exact frozen studies."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from trading.core.accounting import canonical_json_bytes, parse_timestamp
from trading.core.ledger_storage import locked_file
from trading.core.qualification import HistoricalQualificationPlan, StudyQualificationIdentity
from trading.core.qualification_transaction import recover_qualification_plan_transaction
from trading.core.sleeve_engine import (
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    ExecutionCostPolicy,
)
from trading.research_data import (
    ExperimentTrialRegistry,
    QualificationRegistry,
    ResearchDefinitionStore,
)
from trading.research_data.paths import (
    PATH_MIGRATION_REGISTRY,
    ResultPathMigrationError,
    resolve_result_path,
)
from trading.research_data.trial_registry import formal_trial_id
from trading.research_definitions import (
    ResearchDefinitionRegistry,
    resolve_workflow_policy_set,
    resolve_workflow_policy_set_from_release,
)
from trading.workflow.qualification import register_forward_qualification_plan

STUDY_QUALIFICATION_SPEC = "QUALIFICATION_SPEC.json"
STUDY_QUALIFICATION_CAPABILITY = "study-time-retrospective-v1"
FIXED_CALENDAR_RETROSPECTIVE_CAPABILITY = "fixed-calendar-retrospective-v1"
FIXED_CALENDAR_RETROSPECTIVE_ROUTE = "fixed-calendar-retrospective"
FIXED_CALENDAR = {
    "warmup_start": "2013-01-01",
    "warmup_end": "2013-12-31",
    "development_years": [2014, 2015, 2016, 2017, 2018],
    "quarantine_years": [2019],
    "evaluation_years": [2020, 2021, 2022, 2023, 2024],
    "replay_start": "2025-01-01",
    "replay_end": "2025-12-31",
}
CANDIDATE_FREEZE_AUTHORIZATION_SCOPE = (
    "Freeze the exact Development-selected candidate and complete preregistered trial family; "
    "no Evaluation, Shadow, broker, or order authority."
)


def structured_qualification_runtime_contract(workflow_path: Path) -> dict[str, Any]:
    """Return the exact policy, cost, snapshot, and observation contract to preregister."""
    policy_set = resolve_workflow_policy_set_from_release(workflow_path)
    return {
        "policy_set": {
            "identity": policy_set.identity,
            "releases": [
                {
                    "family": release.identity.family,
                    "version": release.identity.version,
                    "path": release.path,
                    "release_digest": release.release_digest,
                    "config_digest": release.config_digest,
                }
                for release in sorted(
                    policy_set.releases,
                    key=lambda item: item.identity.family,
                )
            ],
        },
        "cost_policies": {
            "base": _cost_policy_payload(DEFAULT_BASE_COST_POLICY),
            "stress": _cost_policy_payload(DEFAULT_STRESS_COST_POLICY),
        },
        "evidence_contract": _supported_evidence_contract(),
    }


def _supported_evidence_contract() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "snapshot": {
            "kind": "immutable-research-data-manifest",
            "definition_binding": "exact",
            "evaluation_coverage": "all-frozen-evaluation-sessions",
            "data_cutoff": "frozen-evaluation-end",
        },
        "observation": {
            "allowed_run_modes": ["offline"],
            "outcome_status": "succeeded",
            "validity_status": "valid",
            "observed_at_floor": "frozen-evaluation-end",
        },
    }


def _cost_policy_payload(policy: ExecutionCostPolicy) -> dict[str, float]:
    return {
        "entry_slippage_bps": policy.entry_slippage_bps,
        "exit_slippage_bps": policy.exit_slippage_bps,
        "fee_bps_per_side": policy.fee_bps_per_side,
    }


STRUCTURED_STUDY_ROUTES = frozenset(
    {
        "clean-historical",
        "retrospective-confirmatory",
        "study-time-retrospective",
        FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    }
)
REQUIRED_STUDY_TIME_CHALLENGES = frozenset(
    {
        "cash",
        "family-baseline",
        "random-entry",
        "parameter-perturbation",
        "delayed-entry",
        "higher-costs",
        "worse-fills",
        "missed-entries",
        "market-regimes",
    }
)


def fixed_challenge_method_contract(challenge_id: str) -> dict[str, Any]:
    """Return the complete registered v1 method contract for one fixed-route challenge."""
    parameters: dict[str, Any] = {
        "cash": {"scenario": "base_net", "comparison": "total-return-greater-than-zero"},
        "family-baseline": {
            "scenario": "base_net",
            "comparison": "selected-total-return-greater-than-target",
        },
        "random-entry": {
            "scenario": "base_net",
            "algorithm": "stationary-session-block-bootstrap",
            "seed_source": "benchmarks.random_seed",
            "sample_count_source": "benchmarks.random_samples",
            "block_sessions_source": "benchmarks.bootstrap_block_sessions",
            "comparison": "selected-total-return-greater-than-bootstrap-median",
        },
        "parameter-perturbation": {
            "scenario": "base_net",
            "aggregate": "all-target-total-returns-positive",
        },
        "delayed-entry": {
            "scenario": "base_net",
            "aggregate": "all-target-total-returns-positive",
        },
        "higher-costs": {
            "scenario": "stress_net",
            "requirements": ["total-return-positive", "profit-factor-greater-than-one"],
        },
        "worse-fills": {
            "scenario": "stress_net",
            "entry_transform": "canonical-stress-entry-slippage",
            "exit_transform": "canonical-stress-exit-slippage",
            "rounding": "engine-native-full-precision",
            "gap_handling": "use-frozen-candidate-price",
            "intrabar_ambiguity": "canonical-engine-order",
            "fee_slippage_order": "slippage-then-fee-per-side",
            "unavailable_price": "fail",
            "unfilled": "retain-noncompleted-without-pnl",
            "requirements": ["total-return-positive", "profit-factor-greater-than-one"],
        },
        "missed-entries": {
            "scenario": "base_net",
            "eligible_universe": "completed-selected-evaluation-trades",
            "ordering": ["entry_date", "signal_date", "proposal_terms"],
            "algorithm": "seeded-shuffle-drop-prefix",
            "omission_fraction": "0.10",
            "percentage_to_count_rounding": "floor",
            "seed_source": "benchmarks.random_seed",
            "tie_handling": "canonical-order-before-shuffle",
            "zero_selected_allowed": False,
            "replacement": False,
            "ledger_behavior": "replay-kept-trades-without-replacement",
            "comparison": "kept-trade-pnl-positive",
        },
        "market-regimes": {
            "scenario": "base_net",
            "window": "calendar-quarter",
            "comparison": "positive-quarter-rate-at-least-half",
        },
    }.get(challenge_id, {})
    if not parameters:
        raise ValueError(f"unknown fixed challenge implementation: {challenge_id}")
    return {
        "schema_version": 1,
        "implementation_id": challenge_id,
        "implementation_version": "fixed-challenge-v1",
        "input_schema": "evaluation-role-projection-v1",
        "output_schema": "boolean-gate-observation-v1",
        "parameters": parameters,
        "allowed_dependency_roles": ["warmup"],
        "failure_conditions": [
            "missing-or-duplicate-source",
            "mixed-data-generation",
            "incomplete-evaluation-sessions",
            "identity-or-policy-drift",
            "role-leakage",
        ],
    }


def validate_study_qualification_spec_for_preregistration(
    study_path: Path,
) -> str:
    """Validate the outcome-free structured contract and return its exact digest."""
    study = Path(study_path).resolve()
    payload = _json_object(study / STUDY_QUALIFICATION_SPEC)
    if payload.get("schema_version") != 1:
        raise ValueError("QUALIFICATION_SPEC.json schema_version must be 1")
    expected_study = study.relative_to(study.parents[4]).as_posix()
    if payload.get("study_path") != expected_study:
        raise ValueError("QUALIFICATION_SPEC.json belongs to a different study")
    route = payload.get("route")
    if route not in STRUCTURED_STUDY_ROUTES:
        raise ValueError("QUALIFICATION_SPEC.json has an invalid route")
    registries = _mapping(payload.get("registries"), "registries")
    for field in ("trial_registry_path", "qualification_registry_path"):
        identity = registries.get(field)
        if (
            not isinstance(identity, str)
            or not identity.strip()
            or not _is_safe_repo_relative(identity)
        ):
            raise ValueError(f"QUALIFICATION_SPEC.json {field} is invalid")
    if registries["trial_registry_path"] == registries["qualification_registry_path"]:
        raise ValueError("QUALIFICATION_SPEC.json registry identities must be distinct")
    policy_set = _mapping(payload.get("policy_set"), "policy set")
    if not _is_sha256(policy_set.get("identity")):
        raise ValueError("QUALIFICATION_SPEC.json policy-set identity is invalid")
    policy_releases = policy_set.get("releases")
    if (
        not isinstance(policy_releases, list)
        or len(policy_releases) != 4
        or not all(isinstance(item, dict) for item in policy_releases)
    ):
        raise ValueError("QUALIFICATION_SPEC.json must freeze four policy releases")
    policy_families = tuple(str(item.get("family")) for item in policy_releases)
    if (
        policy_families != tuple(sorted(policy_families))
        or len(set(policy_families)) != len(policy_families)
        or any(
            not isinstance(item.get("family"), str)
            or not str(item["family"]).strip()
            or not isinstance(item.get("version"), str)
            or not str(item["version"]).strip()
            or not isinstance(item.get("path"), str)
            or not _is_safe_repo_relative(str(item["path"]))
            or not _is_sha256(item.get("release_digest"))
            or not _is_sha256(item.get("config_digest"))
            for item in policy_releases
        )
    ):
        raise ValueError("QUALIFICATION_SPEC.json policy release inventory is invalid")
    policy_identity_payload = [
        {
            "family": item["family"],
            "version": item["version"],
            "release_digest": item["release_digest"],
            "config_digest": item["config_digest"],
        }
        for item in policy_releases
    ]
    if (
        policy_set.get("identity")
        != hashlib.sha256(canonical_json_bytes(policy_identity_payload)).hexdigest()
    ):
        raise ValueError("QUALIFICATION_SPEC.json policy-set identity conflicts with releases")
    try:
        released_policy_set = structured_qualification_runtime_contract(study.parents[2])[
            "policy_set"
        ]
    except ValueError as exc:
        raise ValueError(f"cannot verify released workflow policy set: {exc}") from exc
    if policy_set != released_policy_set:
        raise ValueError("QUALIFICATION_SPEC.json policy set differs from released workflow")
    cost_policies = _mapping(payload.get("cost_policies"), "cost policies")
    base_cost = _execution_cost_policy(cost_policies.get("base"), "base cost policy")
    stress_cost = _execution_cost_policy(cost_policies.get("stress"), "stress cost policy")
    if (
        stress_cost.entry_slippage_bps < base_cost.entry_slippage_bps
        or stress_cost.exit_slippage_bps < base_cost.exit_slippage_bps
        or stress_cost.fee_bps_per_side < base_cost.fee_bps_per_side
    ):
        raise ValueError("QUALIFICATION_SPEC.json stress costs cannot be weaker than base costs")
    evidence_contract = _mapping(payload.get("evidence_contract"), "evidence contract")
    if evidence_contract != _supported_evidence_contract():
        raise ValueError("QUALIFICATION_SPEC.json snapshot/observation contract is unsupported")
    classification = payload.get("evidence_classification")
    if route == "clean-historical":
        if classification != "verified-clean":
            raise ValueError("clean Historical Evaluation requires verified-clean provenance")
    elif classification not in {"known-contaminated", "provenance-unknown"}:
        raise ValueError("retrospective Evaluation cannot claim verified-clean provenance")
    if not str(payload.get("evidence_justification") or "").strip():
        raise ValueError("QUALIFICATION_SPEC.json needs a provenance justification")
    trial_history_complete = _boolean(
        payload.get("trial_history_complete"), "trial history completeness"
    )
    if route == "clean-historical" and not trial_history_complete:
        raise ValueError("clean Historical Evaluation requires complete trial history")
    _boolean(
        payload.get("prior_selection_history_incomplete"),
        "prior selection history disclosure",
    )
    calendar = _mapping(payload.get("calendar"), "calendar")
    if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE and calendar != FIXED_CALENDAR:
        raise ValueError(
            "fixed-calendar-retrospective calendar must match the released 2013-2025 contract"
        )
    development_years = _years(calendar.get("development_years"), "Development")
    evaluation_years = _years(calendar.get("evaluation_years"), "Evaluation")
    quarantine_years = _years(calendar.get("quarantine_years"), "quarantine", allow_empty=True)
    try:
        warmup_start = date.fromisoformat(str(calendar["warmup_start"]))
        warmup_end = date.fromisoformat(str(calendar["warmup_end"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("QUALIFICATION_SPEC.json warmup bounds are invalid") from exc
    if warmup_start > warmup_end or warmup_end.year >= evaluation_years[0]:
        raise ValueError("warmup must be ordered and precede Evaluation")
    if len(development_years) < 3 or len(evaluation_years) < 5:
        raise ValueError("qualification route requires three Development years and five folds")
    role_years = set(development_years) | set(evaluation_years) | set(quarantine_years)
    if len(role_years) != len(development_years) + len(evaluation_years) + len(quarantine_years):
        raise ValueError("Development, Evaluation, and quarantine years must not overlap")
    if route in {
        "clean-historical",
        "study-time-retrospective",
        FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    }:
        if warmup_end.year >= development_years[0]:
            raise ValueError("warmup must precede Development")
        if evaluation_years[0] <= development_years[-1]:
            raise ValueError("Evaluation must follow Development")
        if quarantine_years != tuple(range(development_years[-1] + 1, evaluation_years[0])):
            raise ValueError("every unassigned year must be explicitly quarantined")

    family = _mapping(payload.get("family"), "family")
    members = family.get("members")
    if (
        not isinstance(members, list)
        or not members
        or not all(isinstance(item, dict) for item in members)
    ):
        raise ValueError("QUALIFICATION_SPEC.json family members are malformed")
    identities = tuple(item.get("identity") for item in members)
    if (
        any(not isinstance(identity, str) or not identity.strip() for identity in identities)
        or len(set(identities)) != len(identities)
        or any(not _is_sha256(item.get("source_sha256")) for item in members)
    ):
        raise ValueError("QUALIFICATION_SPEC.json family identities/source digests are invalid")
    typed_identities = tuple(str(identity) for identity in identities)
    roles = tuple(item.get("role") for item in members)
    if any(role not in {"selection-candidate", "family-baseline", "robustness"} for role in roles):
        raise ValueError("QUALIFICATION_SPEC.json family member role is invalid")
    if _positive_int(family.get("maximum_trials"), "maximum trials") != len(typed_identities):
        raise ValueError("QUALIFICATION_SPEC.json must freeze the complete trial family")
    baseline_identity = str(family.get("baseline_identity"))
    if baseline_identity not in typed_identities:
        raise ValueError("QUALIFICATION_SPEC.json baseline is outside the family")
    if (
        roles.count("family-baseline") != 1
        or roles[typed_identities.index(baseline_identity)] != "family-baseline"
    ):
        raise ValueError("QUALIFICATION_SPEC.json needs one exact family baseline role")
    if roles.count("selection-candidate") != 1:
        raise ValueError("QUALIFICATION_SPEC.json needs one exact selection-candidate role")
    shared_sources = family.get("shared_sources")
    if not isinstance(shared_sources, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and bool(item["path"].strip())
        and _is_safe_repo_relative(item["path"])
        and _is_sha256(item.get("sha256"))
        for item in shared_sources
    ):
        raise ValueError("QUALIFICATION_SPEC.json shared source inventory is invalid")
    shared_paths = [str(item["path"]) for item in shared_sources]
    if len(shared_paths) != len(set(shared_paths)):
        raise ValueError("QUALIFICATION_SPEC.json shared source paths must be unique")

    execution = _mapping(payload.get("execution"), "execution")
    maximum_holding = _nonnegative_int(execution.get("maximum_holding_sessions"), "maximum holding")
    execution_lag = _nonnegative_int(execution.get("execution_lag_sessions"), "execution lag")
    dependency = _nonnegative_int(execution.get("dependency_sessions"), "dependency")
    embargo = _nonnegative_int(execution.get("embargo_sessions"), "embargo")
    if dependency < maximum_holding + execution_lag or embargo < execution_lag:
        raise ValueError("QUALIFICATION_SPEC.json execution dependencies are unsafe")
    try:
        drawdown = Decimal(str(execution["stress_drawdown_limit"]))
    except (KeyError, InvalidOperation) as exc:
        raise ValueError("QUALIFICATION_SPEC.json stress drawdown limit is invalid") from exc
    if drawdown <= 0 or drawdown >= 1:
        raise ValueError("QUALIFICATION_SPEC.json stress drawdown limit must be between 0 and 1")
    benchmarks = _mapping(payload.get("benchmarks"), "benchmarks")
    if type(benchmarks.get("random_seed")) is not int:
        raise ValueError("QUALIFICATION_SPEC.json random seed must be an integer")
    for field, label in (
        ("random_samples", "random samples"),
        ("bootstrap_repetitions", "bootstrap repetitions"),
        ("bootstrap_block_sessions", "bootstrap block sessions"),
    ):
        _positive_int(benchmarks.get(field), label)

    challenges = payload.get("required_challenges")
    if not isinstance(challenges, list) or not all(isinstance(item, dict) for item in challenges):
        raise ValueError("QUALIFICATION_SPEC.json challenge inventory is malformed")
    challenge_ids = [str(item.get("id")) for item in challenges]
    if (
        len(challenge_ids) != len(REQUIRED_STUDY_TIME_CHALLENGES)
        or len(set(challenge_ids)) != len(challenge_ids)
        or set(challenge_ids) != REQUIRED_STUDY_TIME_CHALLENGES
    ):
        raise ValueError("QUALIFICATION_SPEC.json required challenge inventory is incomplete")
    if any(not _typed_gate(item.get("gate")) for item in challenges):
        raise ValueError("every required challenge needs a typed per-study gate")
    evidence_identities = [item.get("evidence_identity") for item in challenges]
    if any(not isinstance(item, str) or not item.strip() for item in evidence_identities) or len(
        evidence_identities
    ) != len(set(evidence_identities)):
        raise ValueError("every required challenge needs a unique frozen evidence identity")
    for challenge in challenges:
        applies_to = challenge.get("applies_to")
        if not isinstance(applies_to, dict):
            raise ValueError("every required challenge needs a frozen applies_to identity")
        identity_kind = applies_to.get("kind")
        applied_identities = applies_to.get("identities")
        if (
            identity_kind not in {"benchmark", "trial", "family", "method"}
            or not isinstance(applied_identities, list)
            or not applied_identities
            or not all(isinstance(item, str) and item.strip() for item in applied_identities)
            or len(applied_identities) != len(set(applied_identities))
        ):
            raise ValueError("required challenge applies_to identity is malformed")
        challenge_id = str(challenge["id"])
        expected_target = {
            "cash": ("benchmark", ("cash",)),
            "family-baseline": ("trial", (baseline_identity,)),
            "random-entry": ("benchmark", ("random-entry",)),
        }.get(challenge_id)
        actual_target = (identity_kind, tuple(applied_identities))
        if expected_target is not None and actual_target != expected_target:
            raise ValueError(f"{challenge_id} challenge has the wrong frozen target")
        if expected_target is None and identity_kind != "method":
            raise ValueError(f"{challenge_id} challenge must freeze a method identity")
        if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE:
            if challenge.get("method") != fixed_challenge_method_contract(challenge_id):
                raise ValueError(
                    f"{challenge_id} challenge lacks the registered executable method contract"
                )
    challenge_targets = [
        (
            item["applies_to"]["kind"],
            tuple(item["applies_to"]["identities"]),
        )
        for item in challenges
    ]
    if len(challenge_targets) != len(set(challenge_targets)):
        raise ValueError("required challenges must freeze distinct target identities")
    return _sha256(study / STUDY_QUALIFICATION_SPEC)


def validate_candidate_freeze_for_study(
    study_path: Path,
    payload: dict[str, Any],
) -> None:
    """Validate an exact guarded candidate freeze before or after its add-only write."""
    study = Path(study_path).resolve()
    validate_study_qualification_spec_for_preregistration(study)
    spec = _json_object(study / STUDY_QUALIFICATION_SPEC)
    preregistration = _json_object(study / "PREREGISTRATION.json")
    development_authorization = _json_object(study / "DEVELOPMENT_AUTHORIZATION.json")
    release_path = study.parents[2] / "RELEASE.json"
    expected = {
        "schema_version": 1,
        "study_id": preregistration.get("study_id"),
        "study_path": preregistration.get("study_path"),
        "workflow": preregistration.get("workflow"),
        "workflow_version": preregistration.get("workflow_version"),
        "route": preregistration.get("route"),
        "hypothesis_sha256": _sha256(study / "HYPOTHESIS.md"),
        "plan_sha256": _sha256(study / "PLAN.md"),
        "qualification_spec_sha256": _sha256(study / STUDY_QUALIFICATION_SPEC),
        "preregistration_sha256": _sha256(study / "PREREGISTRATION.json"),
        "workflow_release_sha256": _sha256(release_path),
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        raise ValueError("candidate freeze differs from the exact authorized study")
    if preregistration.get("qualification_spec_sha256") != expected["qualification_spec_sha256"]:
        raise ValueError("preregistration does not pin QUALIFICATION_SPEC.json")
    if preregistration.get("hypothesis_sha256") != expected["hypothesis_sha256"]:
        raise ValueError("study HYPOTHESIS differs from PREREGISTRATION.json")
    if preregistration.get("plan_sha256") != expected["plan_sha256"]:
        raise ValueError("study PLAN differs from PREREGISTRATION.json")
    _validate_development_authorization(
        development_authorization,
        study=study,
        route=str(spec.get("route")),
        preregistration_sha256=str(expected["preregistration_sha256"]),
        preregistered_by=preregistration.get("approved_by"),
    )
    _validate_candidate_freeze_approval(
        payload,
        study=study,
        preregistration=preregistration,
        development_authorization=development_authorization,
    )
    if payload.get("authorization_scope") != CANDIDATE_FREEZE_AUTHORIZATION_SCOPE:
        raise ValueError("candidate freeze authorization scope is not the guarded narrow scope")
    if payload.get("development_authorization_sha256") != _sha256(
        study / "DEVELOPMENT_AUTHORIZATION.json"
    ):
        raise ValueError("candidate freeze differs from the exact Development authorization")

    family = _mapping(spec.get("family"), "family")
    members = family.get("members")
    if not isinstance(members, list) or not all(isinstance(item, dict) for item in members):
        raise ValueError("qualification spec family members are malformed")
    expected_identities = tuple(str(item.get("identity")) for item in members)
    maximum_trials = _positive_int(family.get("maximum_trials"), "maximum trials")
    if payload.get("frozen_trial_budget") != maximum_trials:
        raise ValueError("candidate freeze trial budget differs from qualification spec")
    complete_family = payload.get("complete_family")
    if (
        not isinstance(complete_family, list)
        or len(complete_family) != maximum_trials
        or not all(isinstance(item, dict) for item in complete_family)
    ):
        raise ValueError("candidate freeze must include the complete trial family")
    observed_identities = tuple(str(item.get("source_identity")) for item in complete_family)
    if observed_identities != expected_identities or len(set(observed_identities)) != len(
        observed_identities
    ):
        raise ValueError("candidate freeze family differs from preregistered family order")
    trial_ids = tuple(str(item.get("trial_id")) for item in complete_family)
    if len(set(trial_ids)) != len(trial_ids):
        raise ValueError("candidate freeze family trial ids must be unique")
    for item in complete_family:
        if set(item) != {"source_identity", "trial_id", "definition_fingerprint"}:
            raise ValueError("candidate freeze family member fields are invalid")
        if not isinstance(item.get("trial_id"), str) or not str(item["trial_id"]).strip():
            raise ValueError("candidate freeze family member needs a trial id")
        if not _is_sha256(item.get("definition_fingerprint")):
            raise ValueError("candidate freeze family member fingerprint is invalid")

    selected = _mapping(payload.get("selected_candidate"), "selected candidate")
    baseline = _mapping(payload.get("family_baseline"), "family baseline")
    member_roles = {str(item["identity"]): str(item["role"]) for item in members}
    candidate_identity = next(
        identity for identity, role in member_roles.items() if role == "selection-candidate"
    )
    baseline_identity = str(family.get("baseline_identity"))
    by_identity = {str(item["source_identity"]): item for item in complete_family}
    if selected != by_identity.get(candidate_identity):
        raise ValueError("selected candidate differs from the preregistered candidate role")
    if baseline != by_identity.get(baseline_identity):
        raise ValueError("family baseline differs from the preregistered baseline role")


_LEGACY_S004_SUFFIX = (
    "workflows/strategy-forward-replication-research--v004/work/studies/"
    "fxi-atr-band-mean-reversion-forward-replication--s004"
)


@dataclass(frozen=True, slots=True)
class FrozenStudyQualificationSpec:
    """All outcome-free inputs derived from one immutable study lineage."""

    study_path: Path
    workflow_path: Path
    route: str
    evidence_role: str
    evidence_classification: str
    evidence_justification: str
    trial_history_complete: bool
    prior_selection_history_incomplete: bool
    research_identity: str
    family_baseline_research_identity: str
    selected_trial_id: str
    family_baseline_trial_id: str
    family_research_identities: tuple[str, ...]
    family_trial_ids: dict[str, str] | None
    family_source_sha256: dict[str, str]
    shared_source_sha256: dict[str, str]
    policy_set_identity: str
    policy_releases: tuple[tuple[str, str, str, str, str], ...]
    base_cost_policy: ExecutionCostPolicy
    stress_cost_policy: ExecutionCostPolicy
    evidence_contract_sha256: str
    maximum_family_trials: int
    evaluation_years: tuple[int, ...]
    development_years: tuple[int, ...]
    warmup_start: date
    warmup_end: date
    quarantine_years: tuple[int, ...]
    replay_start: date | None
    replay_end: date | None
    maximum_holding_sessions: int
    execution_lag_sessions: int
    dependency_sessions: int
    embargo_sessions: int
    stress_drawdown_limit: str
    random_seed: int
    random_samples: int
    bootstrap_repetitions: int
    bootstrap_block_sessions: int
    selected_definition_fingerprint: str
    baseline_definition_fingerprint: str
    trial_registry_identity: str | None
    qualification_registry_identity: str | None
    study_identity: StudyQualificationIdentity


def compile_study_qualification_plan(
    *,
    study_path: Path,
    qualification_registry_path: Path,
    trial_registry_path: Path,
    dry_run: bool,
    approved_by: str | None = None,
    contamination_declaration: str | None = None,
    now: Any = None,
    definition_store: ResearchDefinitionStore | None = None,
) -> HistoricalQualificationPlan:
    """Resolve and compile an exact study; callers cannot override frozen inputs."""
    if not dry_run and not str(approved_by or "").strip():
        raise ValueError("study qualification registration requires separate --approved-by")
    if not dry_run and not str(contamination_declaration or "").strip():
        raise ValueError("study qualification registration requires a contamination declaration")
    spec = load_frozen_study_qualification_spec(study_path)
    trial_registry_identity = getattr(spec, "trial_registry_identity", None)
    qualification_registry_identity = getattr(spec, "qualification_registry_identity", None)
    if trial_registry_identity is not None:
        root = spec.study_path.parents[4]
        declared_trial_registry = (root / trial_registry_identity).resolve()
        if (
            Path(trial_registry_path).resolve() == declared_trial_registry
            or not (root / PATH_MIGRATION_REGISTRY).is_file()
        ):
            expected_trial_registry = declared_trial_registry
        else:
            try:
                expected_trial_registry = resolve_result_path(
                    declared_trial_registry,
                    repository_root=root,
                )
            except ResultPathMigrationError as exc:
                raise ValueError(str(exc)) from exc
        expected_qualification_registry = (root / str(qualification_registry_identity)).resolve()
        if Path(trial_registry_path).resolve() != expected_trial_registry:
            raise ValueError("trial registry path differs from frozen qualification spec")
        if Path(qualification_registry_path).resolve() != expected_qualification_registry:
            raise ValueError("qualification registry path differs from frozen qualification spec")
    _verify_frozen_definitions(spec, definition_store=definition_store)
    if dry_run:
        return _compile_spec(
            spec,
            qualification_registry_path=qualification_registry_path,
            trial_registry_path=trial_registry_path,
            dry_run=True,
            now=now,
            definition_store=definition_store,
        )
    registration_lock = qualification_study_registration_lock_path(qualification_registry_path)
    with locked_file(registration_lock, 10.0):
        if (Path(study_path).resolve() / "COMPLETION.json").exists():
            raise ValueError("completed study cannot register a qualification plan")
        current_spec = load_frozen_study_qualification_spec(study_path)
        if current_spec != spec:
            raise ValueError("frozen study changed while qualification registration was waiting")
        _verify_frozen_definitions(current_spec, definition_store=definition_store)
        spec = current_spec
        recovered = recover_qualification_plan_transaction(
            qualification_registry_path,
            expected_study_path=spec.study_identity.study_path,
            expected_trial_registry_path=trial_registry_path,
            expected_qualification_registry_path=qualification_registry_path,
            expected_approved_by=str(approved_by).strip(),
            expected_contamination_declaration=str(contamination_declaration).strip(),
        )
        if recovered is not None:
            return recovered
        existing = _registered_plan_for_study(
            qualification_registry_path,
            study_path=spec.study_identity.study_path,
            trial_registry_path=trial_registry_path,
            approved_by=str(approved_by).strip(),
            contamination_declaration=str(contamination_declaration).strip(),
        )
        if existing is not None:
            return existing
        clock = now or (lambda: datetime.now(UTC))
        started_at = clock()
        if started_at.tzinfo is None:
            raise ValueError("study qualification plan clock must be timezone-aware")
        approved_identity = replace(
            spec.study_identity,
            operation_approved_by=str(approved_by).strip(),
            operation_approved_at=started_at.astimezone(UTC),
            contamination_declaration=str(contamination_declaration).strip(),
            trial_registry_path=str(Path(trial_registry_path).resolve()),
            qualification_registry_path=str(Path(qualification_registry_path).resolve()),
            trial_registry_identity=trial_registry_identity,
            qualification_registry_identity=qualification_registry_identity,
        )
        return _compile_spec(
            replace(spec, study_identity=approved_identity),
            qualification_registry_path=qualification_registry_path,
            trial_registry_path=trial_registry_path,
            dry_run=False,
            now=lambda: started_at,
            definition_store=definition_store,
        )


def frozen_study_qualification_registry_path(study_path: Path) -> Path:
    """Resolve the preregistered authoritative qualification registry without a freeze."""
    study = Path(study_path).resolve()
    payload = _json_object(study / STUDY_QUALIFICATION_SPEC)
    registries = _mapping(payload.get("registries"), "registries")
    identity = registries.get("qualification_registry_path")
    if not isinstance(identity, str) or not _is_safe_repo_relative(identity):
        raise ValueError("QUALIFICATION_SPEC.json qualification_registry_path is invalid")
    return (study.parents[4] / identity).resolve()


def qualification_study_registration_lock_path(registry_path: Path) -> Path:
    """Return the lock shared by plan registration and Development completion."""
    path = Path(registry_path)
    return path.with_name(f".{path.name}.study-registration.lock")


def _compile_spec(
    spec: FrozenStudyQualificationSpec,
    *,
    qualification_registry_path: Path,
    trial_registry_path: Path,
    dry_run: bool,
    now: Any,
    definition_store: ResearchDefinitionStore | None,
) -> HistoricalQualificationPlan:
    state = ExperimentTrialRegistry(trial_registry_path).read()
    if state.get("selection_history_incomplete") is not spec.prior_selection_history_incomplete:
        raise ValueError("trial registry selection-history disclosure differs from frozen study")
    return register_forward_qualification_plan(
        research_identity=spec.research_identity,
        workflow_path=spec.workflow_path,
        family_baseline_trial_id=spec.family_baseline_trial_id,
        evaluation_years=spec.evaluation_years,
        maximum_holding_sessions=spec.maximum_holding_sessions,
        execution_lag_sessions=spec.execution_lag_sessions,
        dependency_sessions=spec.dependency_sessions,
        embargo_sessions=spec.embargo_sessions,
        stress_drawdown_limit=spec.stress_drawdown_limit,
        random_seed=spec.random_seed,
        random_samples=spec.random_samples,
        bootstrap_repetitions=spec.bootstrap_repetitions,
        bootstrap_block_sessions=spec.bootstrap_block_sessions,
        qualification_registry_path=qualification_registry_path,
        trial_registry_path=trial_registry_path,
        now=now,
        definition_store=definition_store,
        evidence_role=spec.evidence_role,
        evidence_classification=spec.evidence_classification,
        evidence_justification=spec.evidence_justification,
        trial_history_complete=spec.trial_history_complete,
        development_years=spec.development_years,
        warmup_start=spec.warmup_start,
        warmup_end=spec.warmup_end,
        quarantine_years=spec.quarantine_years,
        family_research_identities=spec.family_research_identities,
        dry_run=dry_run,
        family_source_sha256=spec.family_source_sha256,
        maximum_family_trials=spec.maximum_family_trials,
        study_identity=spec.study_identity,
        base_cost_policy=spec.base_cost_policy,
        stress_cost_policy=spec.stress_cost_policy,
    )


def _registered_plan_for_study(
    qualification_registry_path: Path,
    *,
    study_path: str,
    trial_registry_path: Path,
    approved_by: str,
    contamination_declaration: str,
) -> HistoricalQualificationPlan | None:
    registry = QualificationRegistry(qualification_registry_path)
    state = registry.read()
    events = state.get("events")
    if not isinstance(events, list):
        return None
    matches: list[str] = []
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "historical_plan":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        identity = payload.get("study_identity")
        if isinstance(identity, dict) and identity.get("study_path") == study_path:
            plan_id = payload.get("plan_id")
            if isinstance(plan_id, str):
                matches.append(plan_id)
    if len(matches) > 1:
        raise ValueError("study has more than one registered qualification plan")
    if not matches:
        return None
    plan = registry.historical_plan(matches[0])
    identity = plan.study_identity
    if (
        identity is None
        or identity.trial_registry_path != str(Path(trial_registry_path).resolve())
        or identity.qualification_registry_path != str(Path(qualification_registry_path).resolve())
        or identity.operation_approved_by != approved_by
        or identity.contamination_declaration != contamination_declaration
    ):
        raise ValueError("existing study qualification plan belongs to a different operation")
    return plan


def load_frozen_study_qualification_spec(study_path: Path) -> FrozenStudyQualificationSpec:
    """Load a structured future spec or the one exact backward-compatible S004 adapter."""
    study = Path(study_path).resolve()
    if (study / STUDY_QUALIFICATION_SPEC).is_file():
        return _load_structured_spec(study)
    if study == _canonical_legacy_s004_path():
        return _load_legacy_s004(study)
    raise ValueError("study has no frozen QUALIFICATION_SPEC.json")


def _canonical_legacy_s004_path() -> Path:
    """Resolve S004 only inside the current canonical repository checkout."""
    current = Path.cwd().resolve()
    for root in (current, *current.parents):
        if (root / ".git").exists() and (root / "workflows" / "README.md").is_file():
            return (root / _LEGACY_S004_SUFFIX).resolve()
    raise ValueError("cannot resolve the canonical repository for legacy S004")


def _load_legacy_s004(study: Path) -> FrozenStudyQualificationSpec:
    preregistration = _json_object(study / "PREREGISTRATION.json")
    candidate_freeze = _json_object(study / "CANDIDATE_FREEZE.json")
    plan_path = study / "PLAN.md"
    workflow = study.parents[2]
    release_path = workflow / "RELEASE.json"
    plan_sha = _sha256(plan_path)
    prereg_sha = _sha256(study / "PREREGISTRATION.json")
    freeze_sha = _sha256(study / "CANDIDATE_FREEZE.json")
    release_sha = _sha256(release_path)
    release = _json_object(release_path)
    runtime_contract = structured_qualification_runtime_contract(workflow)
    legacy_policy_set = _mapping(runtime_contract["policy_set"], "policy set")
    legacy_policy_releases = legacy_policy_set["releases"]
    if preregistration.get("plan_sha256") != plan_sha:
        raise ValueError("study PLAN differs from PREREGISTRATION.json")
    if candidate_freeze.get("preregistration_sha256") != prereg_sha:
        raise ValueError("candidate freeze differs from exact preregistration")
    if candidate_freeze.get("plan_sha256") != plan_sha:
        raise ValueError("candidate freeze differs from exact PLAN")
    if preregistration.get("workflow_sha256") != release.get("workflow_sha256"):
        raise ValueError("preregistration workflow differs from released workflow")
    plan = plan_path.read_text(encoding="utf-8")
    _require_text(plan, release_sha)
    _require_text(plan, "`maximum_trials=6`")
    _require_text(plan, "2015-01-02 through 2025-12-31")
    _require_text(plan, "Every 2026 session")
    _require_text(plan, "2027, 2028, 2029, 2030, 2031")
    _require_text(plan, "seed `20260813`")
    _require_text(plan, "1,000 replicas")

    identities = (
        "fxi-atr-band-mean-reversion/atr-band-candidate",
        "fxi-atr-band-mean-reversion/pullback-wr-baseline",
        "fxi-atr-band-mean-reversion/atr-floor-1p10-robustness",
        "fxi-atr-band-mean-reversion/atr-ceiling-1p30-robustness",
        "fxi-atr-band-mean-reversion/hold-18-robustness",
        "fxi-atr-band-mean-reversion/delay-one-session-robustness",
    )
    source_hashes = _source_hash_table(plan, identities)
    shared_path = "src/trading/research_definitions/fxi_mean_reversion.py"
    shared_match = re.search(
        rf"shared `{re.escape(shared_path)}` runtime \| `([0-9a-f]{{64}})`",
        plan,
    )
    if shared_match is None:
        raise ValueError("S004 PLAN does not pin the shared runtime digest")
    selected = _mapping(candidate_freeze.get("selected_candidate"), "selected candidate")
    baseline = _mapping(candidate_freeze.get("family_baseline"), "family baseline")
    if selected.get("source_identity") != identities[0]:
        raise ValueError("candidate freeze selected identity differs from PLAN")
    if baseline.get("source_identity") != identities[1]:
        raise ValueError("candidate freeze baseline identity differs from PLAN")
    if candidate_freeze.get("frozen_trial_budget") != 6:
        raise ValueError("candidate freeze trial budget differs from PLAN")
    if (
        tuple(candidate_freeze.get("robustness_source_inventory_pinned_by_plan", ()))
        != identities[2:]
    ):
        raise ValueError("candidate freeze robustness family differs from PLAN")
    return FrozenStudyQualificationSpec(
        study_path=study,
        workflow_path=workflow,
        route="clean-historical",
        evidence_role="historical",
        evidence_classification="verified-clean",
        evidence_justification=(
            "The preregistered 2027-2031 folds were reserved before their outcomes; "
            "legacy selection history remains explicitly incomplete."
        ),
        trial_history_complete=True,
        prior_selection_history_incomplete=True,
        research_identity=identities[0],
        family_baseline_research_identity=identities[1],
        selected_trial_id=str(selected["trial_id"]),
        family_baseline_trial_id=str(baseline["trial_id"]),
        family_research_identities=identities,
        family_trial_ids=None,
        family_source_sha256=source_hashes,
        shared_source_sha256={shared_path: shared_match.group(1)},
        policy_set_identity=str(legacy_policy_set["identity"]),
        policy_releases=_policy_release_identities(legacy_policy_releases),
        base_cost_policy=DEFAULT_BASE_COST_POLICY,
        stress_cost_policy=DEFAULT_STRESS_COST_POLICY,
        evidence_contract_sha256=hashlib.sha256(
            canonical_json_bytes(runtime_contract["evidence_contract"])
        ).hexdigest(),
        maximum_family_trials=6,
        evaluation_years=(2027, 2028, 2029, 2030, 2031),
        development_years=tuple(range(2015, 2026)),
        warmup_start=date(2013, 11, 6),
        warmup_end=date(2014, 12, 31),
        quarantine_years=(2026,),
        replay_start=None,
        replay_end=None,
        maximum_holding_sessions=20,
        execution_lag_sessions=1,
        dependency_sessions=21,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        random_seed=20260813,
        random_samples=1000,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=20,
        selected_definition_fingerprint=str(selected["definition_fingerprint"]),
        baseline_definition_fingerprint=str(baseline["definition_fingerprint"]),
        trial_registry_identity=None,
        qualification_registry_identity=None,
        study_identity=StudyQualificationIdentity(
            study_path=str(preregistration["study_path"]),
            preregistration_sha256=prereg_sha,
            plan_sha256=plan_sha,
            candidate_freeze_sha256=freeze_sha,
            qualification_spec_sha256=None,
            workflow_release_sha256=release_sha,
        ),
    )


def _load_structured_spec(study: Path) -> FrozenStudyQualificationSpec:
    validate_study_qualification_spec_for_preregistration(study)
    payload = _json_object(study / STUDY_QUALIFICATION_SPEC)
    preregistration = _json_object(study / "PREREGISTRATION.json")
    candidate_freeze = _json_object(study / "CANDIDATE_FREEZE.json")
    validate_candidate_freeze_for_study(study, candidate_freeze)
    workflow = study.parents[2]
    release = _json_object(workflow / "RELEASE.json")
    capabilities = release.get("capabilities")
    required_capability = (
        FIXED_CALENDAR_RETROSPECTIVE_CAPABILITY
        if payload.get("route") == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
        else STUDY_QUALIFICATION_CAPABILITY
    )
    if not isinstance(capabilities, list) or required_capability not in capabilities:
        raise ValueError("released workflow lacks the route's structured qualification capability")
    spec_sha = _sha256(study / STUDY_QUALIFICATION_SPEC)
    preregistration_sha = _sha256(study / "PREREGISTRATION.json")
    plan_sha = _sha256(study / "PLAN.md")
    if preregistration.get("qualification_spec_sha256") != spec_sha:
        raise ValueError("preregistration does not pin QUALIFICATION_SPEC.json")
    if candidate_freeze.get("qualification_spec_sha256") != spec_sha:
        raise ValueError("candidate freeze does not pin QUALIFICATION_SPEC.json")
    if preregistration.get("plan_sha256") != plan_sha:
        raise ValueError("study PLAN differs from PREREGISTRATION.json")
    if candidate_freeze.get("preregistration_sha256") != preregistration_sha:
        raise ValueError("candidate freeze differs from exact preregistration")
    if candidate_freeze.get("plan_sha256") != plan_sha:
        raise ValueError("candidate freeze differs from exact PLAN")
    if preregistration.get("workflow_sha256") != release.get("workflow_sha256"):
        raise ValueError("preregistration workflow differs from released workflow")
    if payload.get("study_path") != preregistration.get("study_path"):
        raise ValueError("qualification spec belongs to a different study")
    route = str(payload.get("route"))
    if route not in STRUCTURED_STUDY_ROUTES:
        raise ValueError("structured qualification spec has an invalid route")
    if preregistration.get("route") != route:
        raise ValueError("preregistration route differs from qualification spec")
    calendar = _mapping(payload.get("calendar"), "calendar")
    registries = _mapping(payload.get("registries"), "registries")
    family = _mapping(payload.get("family"), "family")
    execution = _mapping(payload.get("execution"), "execution")
    benchmarks = _mapping(payload.get("benchmarks"), "benchmarks")
    policy_set = _mapping(payload.get("policy_set"), "policy set")
    policy_releases = policy_set.get("releases")
    if not isinstance(policy_releases, list):
        raise ValueError("qualification spec policy releases are malformed")
    cost_policies = _mapping(payload.get("cost_policies"), "cost policies")
    evidence_contract = _mapping(payload.get("evidence_contract"), "evidence contract")
    challenges = payload.get("required_challenges")
    if not isinstance(challenges, list) or not all(isinstance(item, dict) for item in challenges):
        raise ValueError("qualification spec required challenges are malformed")
    challenge_ids = {str(item.get("id")) for item in challenges}
    if challenge_ids != REQUIRED_STUDY_TIME_CHALLENGES:
        raise ValueError("qualification spec required challenge inventory is incomplete")
    if any(not _typed_gate(item.get("gate")) for item in challenges):
        raise ValueError("every required challenge needs a typed per-study gate")
    members = family.get("members")
    if (
        not isinstance(members, list)
        or not members
        or not all(isinstance(item, dict) for item in members)
    ):
        raise ValueError("qualification spec family members are malformed")
    identities = tuple(str(item.get("identity")) for item in members)
    if len(set(identities)) != len(identities):
        raise ValueError("qualification spec family contains duplicate identities")
    maximum_trials = _positive_int(family.get("maximum_trials"), "maximum trials")
    if maximum_trials != len(identities):
        raise ValueError("qualification spec must freeze the complete trial family")
    shared_sources = family.get("shared_sources")
    if not isinstance(shared_sources, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("sha256"), str)
        for item in shared_sources
    ):
        raise ValueError("qualification spec shared source inventory is malformed")
    selected = _mapping(candidate_freeze.get("selected_candidate"), "selected candidate")
    baseline = _mapping(candidate_freeze.get("family_baseline"), "family baseline")
    if (
        selected.get("source_identity") not in identities
        or baseline.get("source_identity") not in identities
    ):
        raise ValueError("candidate freeze identities are outside the frozen family")
    member_roles = {str(item["identity"]): str(item["role"]) for item in members}
    candidate_identity = next(
        identity for identity, role in member_roles.items() if role == "selection-candidate"
    )
    baseline_identity = str(family["baseline_identity"])
    if (
        selected.get("source_identity") != candidate_identity
        or baseline.get("source_identity") != baseline_identity
        or member_roles.get(baseline_identity) != "family-baseline"
        or selected.get("source_identity") == baseline.get("source_identity")
    ):
        raise ValueError("candidate freeze differs from preregistered family roles")
    development_years = _years(calendar.get("development_years"), "Development")
    evaluation_years = _years(calendar.get("evaluation_years"), "Evaluation")
    quarantine_years = _years(calendar.get("quarantine_years"), "quarantine", allow_empty=True)
    if route in {
        "clean-historical",
        "study-time-retrospective",
        FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    }:
        if evaluation_years[0] <= development_years[-1]:
            raise ValueError("Evaluation must follow Development")
        expected_gap = tuple(range(development_years[-1] + 1, evaluation_years[0]))
        if quarantine_years != expected_gap:
            raise ValueError("qualification spec must quarantine every unassigned year")
    evidence_role = "historical" if route == "clean-historical" else route
    return FrozenStudyQualificationSpec(
        study_path=study,
        workflow_path=workflow,
        route=route,
        evidence_role=evidence_role,
        evidence_classification=str(payload.get("evidence_classification")),
        evidence_justification=str(payload.get("evidence_justification")),
        trial_history_complete=bool(payload.get("trial_history_complete", False)),
        prior_selection_history_incomplete=_boolean(
            payload.get("prior_selection_history_incomplete"),
            "prior selection history disclosure",
        ),
        research_identity=str(selected["source_identity"]),
        family_baseline_research_identity=str(baseline["source_identity"]),
        selected_trial_id=str(selected["trial_id"]),
        family_baseline_trial_id=str(baseline["trial_id"]),
        family_research_identities=identities,
        family_trial_ids={
            str(item["source_identity"]): str(item["trial_id"])
            for item in candidate_freeze["complete_family"]
        },
        family_source_sha256={
            str(item["identity"]): str(item["source_sha256"]) for item in members
        },
        shared_source_sha256={str(item["path"]): str(item["sha256"]) for item in shared_sources},
        policy_set_identity=str(policy_set["identity"]),
        policy_releases=_policy_release_identities(policy_releases),
        base_cost_policy=_execution_cost_policy(cost_policies["base"], "base cost policy"),
        stress_cost_policy=_execution_cost_policy(cost_policies["stress"], "stress cost policy"),
        evidence_contract_sha256=hashlib.sha256(
            canonical_json_bytes(evidence_contract)
        ).hexdigest(),
        maximum_family_trials=maximum_trials,
        evaluation_years=evaluation_years,
        development_years=development_years,
        warmup_start=date.fromisoformat(str(calendar["warmup_start"])),
        warmup_end=date.fromisoformat(str(calendar["warmup_end"])),
        quarantine_years=quarantine_years,
        replay_start=(
            date.fromisoformat(str(calendar["replay_start"]))
            if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
            else None
        ),
        replay_end=(
            date.fromisoformat(str(calendar["replay_end"]))
            if route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
            else None
        ),
        maximum_holding_sessions=_nonnegative_int(
            execution.get("maximum_holding_sessions"), "maximum holding"
        ),
        execution_lag_sessions=_nonnegative_int(
            execution.get("execution_lag_sessions"), "execution lag"
        ),
        dependency_sessions=_nonnegative_int(execution.get("dependency_sessions"), "dependency"),
        embargo_sessions=_nonnegative_int(execution.get("embargo_sessions"), "embargo"),
        stress_drawdown_limit=str(execution["stress_drawdown_limit"]),
        random_seed=int(benchmarks["random_seed"]),
        random_samples=_positive_int(benchmarks.get("random_samples"), "random samples"),
        bootstrap_repetitions=_positive_int(
            benchmarks.get("bootstrap_repetitions"), "bootstrap repetitions"
        ),
        bootstrap_block_sessions=_positive_int(
            benchmarks.get("bootstrap_block_sessions"), "bootstrap block sessions"
        ),
        selected_definition_fingerprint=str(selected["definition_fingerprint"]),
        baseline_definition_fingerprint=str(baseline["definition_fingerprint"]),
        trial_registry_identity=str(registries["trial_registry_path"]),
        qualification_registry_identity=str(registries["qualification_registry_path"]),
        study_identity=StudyQualificationIdentity(
            study_path=str(preregistration["study_path"]),
            preregistration_sha256=preregistration_sha,
            plan_sha256=plan_sha,
            candidate_freeze_sha256=_sha256(study / "CANDIDATE_FREEZE.json"),
            qualification_spec_sha256=spec_sha,
            workflow_release_sha256=_sha256(workflow / "RELEASE.json"),
            development_authorization_sha256=_sha256(study / "DEVELOPMENT_AUTHORIZATION.json"),
            policy_set_identity=str(policy_set["identity"]),
            evidence_contract_sha256=hashlib.sha256(
                canonical_json_bytes(evidence_contract)
            ).hexdigest(),
        ),
    )


def _validate_development_authorization(
    payload: dict[str, Any],
    *,
    study: Path,
    route: str,
    preregistration_sha256: str,
    preregistered_by: object,
) -> None:
    relative_study = study.relative_to(study.parents[4]).as_posix()
    expected = {
        "schema_version": 1,
        "study_path": relative_study,
        "route": route,
        "preregistration_sha256": preregistration_sha256,
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        raise ValueError("Development authorization differs from the exact preregistered study")
    try:
        parse_timestamp(str(payload["authorized_at"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("Development authorization time is invalid") from exc
    for field in ("approved_by", "authorized_operator", "authorization_scope"):
        if not isinstance(payload.get(field), str) or not str(payload[field]).strip():
            raise ValueError(f"Development authorization needs {field}")
    if payload.get("approved_by") != preregistered_by:
        raise ValueError("Development authorization approver differs from the human owner")


def _validate_candidate_freeze_approval(
    payload: dict[str, Any],
    *,
    study: Path,
    preregistration: dict[str, Any],
    development_authorization: dict[str, Any],
) -> None:
    expected = {
        "schema_version": 1,
        "study_path": study.relative_to(study.parents[4]).as_posix(),
        "study_id": preregistration.get("study_id"),
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        raise ValueError("candidate freeze identity differs from the exact study")
    if not isinstance(payload.get("approved_by"), str) or not str(payload["approved_by"]).strip():
        raise ValueError("candidate freeze requires human research-owner approval")
    if payload.get("approved_by") != preregistration.get("approved_by"):
        raise ValueError("candidate freeze approver differs from the human research owner")
    if (
        not isinstance(payload.get("authorization_scope"), str)
        or not str(payload["authorization_scope"]).strip()
    ):
        raise ValueError("candidate freeze requires a narrow authorization scope")
    try:
        freeze_time = parse_timestamp(str(payload["approved_at"]))
        preregistration_time = parse_timestamp(str(preregistration["approved_at"]))
        development_time = parse_timestamp(str(development_authorization["authorized_at"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("candidate freeze approval time is invalid") from exc
    if freeze_time < preregistration_time or freeze_time < development_time:
        raise ValueError("candidate freeze approval must follow preregistration and Development")


def _verify_frozen_definitions(
    spec: FrozenStudyQualificationSpec,
    *,
    definition_store: ResearchDefinitionStore | None,
) -> None:
    registry = ResearchDefinitionRegistry()
    policy_set = resolve_workflow_policy_set(spec.workflow_path)
    observed_policy_releases = tuple(
        (
            release.identity.family,
            release.identity.version,
            release.path,
            release.release_digest,
            release.config_digest,
        )
        for release in sorted(policy_set.releases, key=lambda item: item.identity.family)
    )
    if (
        policy_set.identity != spec.policy_set_identity
        or observed_policy_releases != spec.policy_releases
    ):
        raise ValueError("frozen policy-set identity differs from released workflow policies")
    observed_ids: dict[str, str] = {}
    temporary: TemporaryDirectory[str] | None = None
    if definition_store is None:
        temporary = TemporaryDirectory(prefix="study-qualification-verify-")
        definition_store = ResearchDefinitionStore(Path(temporary.name))
    try:
        for identity in spec.family_research_identities:
            source = registry.resolve(identity)
            if _sha256(source) != spec.family_source_sha256[identity]:
                raise ValueError(f"frozen source digest differs for {identity}")
            strategy = registry.load(identity)
            snapshot = strategy.capture_research_definition(definition_store, policy_set)
            declaration = strategy.declare_experiment_trial()
            observed_ids[identity] = formal_trial_id(declaration.family, snapshot.fingerprint)
            if (
                identity == spec.research_identity
                and snapshot.fingerprint != spec.selected_definition_fingerprint
            ):
                raise ValueError("selected candidate fingerprint differs from candidate freeze")
            if (
                observed_ids[identity] == spec.family_baseline_trial_id
                and snapshot.fingerprint != spec.baseline_definition_fingerprint
            ):
                raise ValueError("family baseline fingerprint differs from candidate freeze")
        if spec.family_trial_ids is not None and observed_ids != spec.family_trial_ids:
            raise ValueError("candidate freeze trial ids differ from frozen definitions")
    finally:
        if temporary is not None:
            temporary.cleanup()
    if observed_ids[spec.research_identity] != spec.selected_trial_id:
        raise ValueError("selected trial identity differs from candidate freeze")
    if observed_ids.get(spec.family_baseline_research_identity) != spec.family_baseline_trial_id:
        raise ValueError("family baseline trial identity differs from frozen source")
    for relative, digest in spec.shared_source_sha256.items():
        path = spec.study_path.parents[4] / relative
        if not path.is_file() or _sha256(path) != digest:
            raise ValueError(f"frozen shared source digest differs: {relative}")


def _source_hash_table(plan: str, identities: tuple[str, ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    for identity in identities:
        leaf = identity.rsplit("/", 1)[1]
        match = re.search(rf"`{re.escape(leaf)}/definition\.py` \| `([0-9a-f]{{64}})`", plan)
        if match is None:
            raise ValueError(f"S004 PLAN does not pin source bytes for {identity}")
        result[identity] = match.group(1)
    return result


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read frozen study artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"frozen study artifact must be an object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"qualification spec {name} is malformed")
    return value


def _execution_cost_policy(value: object, name: str) -> ExecutionCostPolicy:
    payload = _mapping(value, name)
    if set(payload) != {
        "entry_slippage_bps",
        "exit_slippage_bps",
        "fee_bps_per_side",
    }:
        raise ValueError(f"qualification spec {name} fields are invalid")
    values = tuple(payload[field] for field in sorted(payload))
    if any(type(item) not in {int, float} or not math.isfinite(float(item)) for item in values):
        raise ValueError(f"qualification spec {name} values are invalid")
    try:
        return ExecutionCostPolicy(
            entry_slippage_bps=float(payload["entry_slippage_bps"]),
            exit_slippage_bps=float(payload["exit_slippage_bps"]),
            fee_bps_per_side=float(payload["fee_bps_per_side"]),
        )
    except ValueError as exc:
        raise ValueError(f"qualification spec {name} values are invalid") from exc


def _policy_release_identities(value: object) -> tuple[tuple[str, str, str, str, str], ...]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("qualification spec policy releases are malformed")
    return tuple(
        (
            str(item["family"]),
            str(item["version"]),
            str(item["path"]),
            str(item["release_digest"]),
            str(item["config_digest"]),
        )
        for item in value
    )


def _years(value: object, name: str, *, allow_empty: bool = False) -> tuple[int, ...]:
    if not isinstance(value, list) or not all(type(item) is int for item in value):
        raise ValueError(f"qualification spec {name} years are malformed")
    years = tuple(value)
    if not years and not allow_empty:
        raise ValueError(f"qualification spec {name} years are empty")
    if years and years != tuple(range(years[0], years[-1] + 1)):
        raise ValueError(f"qualification spec {name} years must be consecutive")
    return years


def _positive_int(value: object, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"qualification spec {name} must be positive")
    return value


def _nonnegative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"qualification spec {name} must be nonnegative")
    return value


def _boolean(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"qualification spec {name} must be boolean")
    return value


def _require_text(text: str, required: str) -> None:
    if required not in text:
        raise ValueError(f"S004 PLAN frozen contract is missing: {required}")


def _typed_gate(value: object) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("metric"), str)
        and bool(value["metric"].strip())
        and value.get("operator") in {"=", "==", "!=", ">", ">=", "<", "<="}
        and "threshold" in value
        and value["threshold"] is not None
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _is_safe_repo_relative(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()

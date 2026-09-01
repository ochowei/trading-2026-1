"""Independent provider-free challenge-only execution for frozen workflow studies."""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import shutil
import tempfile
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from trading.core.accounting import canonical_json_bytes
from trading.core.ledger_storage import locked_file
from trading.core.sleeve_engine import compute_daily_equity_metrics
from trading.research_data import (
    ExperimentTrialRegistry,
    QualificationRegistry,
    ResearchDataStore,
    ResearchDefinitionStore,
)
from trading.research_data.paths import ResultPathMigrationError, resolve_result_path
from trading.research_data.result_schema import _canonical_sleeve_evidence_error
from trading.workflow.study_qualification import (
    FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    REQUIRED_STUDY_TIME_CHALLENGES,
    fixed_challenge_method_contract,
    load_frozen_study_qualification_spec,
)

CHALLENGE_STAGE = "fixed-historical-evaluation-challenges"


def run_fixed_study_challenges(
    *,
    study_path: Path,
    plan_id: str,
    family_manifests: Mapping[str, Path],
    qualification_registry_path: Path,
    trial_registry_path: Path,
    research_data_store: ResearchDataStore,
    output_root: Path | None = None,
    dry_run: bool,
) -> Path:
    """Produce nine challenge artifacts without providers, definitions, screens, or registry writes."""
    study = Path(study_path).resolve()
    root = study.parents[4].resolve()
    spec = load_frozen_study_qualification_spec(study)
    if spec.route != FIXED_CALENDAR_RETROSPECTIVE_ROUTE:
        raise ValueError("challenge-only operation requires fixed-calendar-retrospective route")
    expected_qualification = (root / str(spec.qualification_registry_identity)).resolve()
    expected_trials = (root / str(spec.trial_registry_identity)).resolve()
    if Path(qualification_registry_path).resolve() != expected_qualification:
        raise ValueError("qualification registry path differs from frozen qualification spec")
    if Path(trial_registry_path).resolve() != expected_trials:
        raise ValueError("trial registry path differs from frozen qualification spec")
    plan = QualificationRegistry(expected_qualification).historical_plan(plan_id)
    if (
        plan.evidence_role != FIXED_CALENDAR_RETROSPECTIVE_ROUTE
        or plan.study_identity is None
        or plan.study_identity.study_path != spec.study_identity.study_path
    ):
        raise ValueError("challenge plan does not belong to the fixed-calendar study")
    expected_identities = tuple(spec.family_research_identities)
    if set(family_manifests) != set(expected_identities) or len(family_manifests) != len(
        expected_identities
    ):
        raise ValueError("challenge manifests must cover the exact frozen family once")

    spec_payload = _json_object(study / "QUALIFICATION_SPEC.json")
    frozen_challenges = spec_payload.get("required_challenges")
    if not isinstance(frozen_challenges, list) or len(frozen_challenges) != len(
        REQUIRED_STUDY_TIME_CHALLENGES
    ):
        raise ValueError("fixed challenge inventory is incomplete")
    contracts = {str(item.get("id")): item for item in frozen_challenges if isinstance(item, dict)}
    if set(contracts) != REQUIRED_STUDY_TIME_CHALLENGES:
        raise ValueError("fixed challenge inventory is incomplete")
    for challenge_id, contract in contracts.items():
        if contract.get("method") != fixed_challenge_method_contract(challenge_id):
            raise ValueError(f"{challenge_id} challenge method is not registered")

    trial_state = ExperimentTrialRegistry(expected_trials).read()
    projections = {
        identity: _load_projection(
            root=root,
            identity=identity,
            manifest_path=family_manifests[identity],
            expected_trial_id=_trial_id(spec, identity),
            expected_fingerprint=_fingerprint(spec, identity),
            expected_policy_set=spec.policy_set_identity,
            expected_workflow_path=spec.workflow_path,
            expected_workflow_release_sha256=spec.study_identity.workflow_release_sha256,
            evaluation_sessions=tuple(plan.evaluation_sessions),
            trial_state=trial_state,
            research_data_store=research_data_store,
        )
        for identity in expected_identities
    }
    generations = {item["data_generation"] for item in projections.values()}
    if len(generations) != 1:
        raise ValueError("challenge family uses mixed frozen data generations")

    binding = {
        "study_path": spec.study_identity.study_path,
        "qualification_plan_id": plan_id,
        "qualification_spec_sha256": spec.study_identity.qualification_spec_sha256,
        "candidate_freeze_sha256": spec.study_identity.candidate_freeze_sha256,
        "workflow_release_sha256": spec.study_identity.workflow_release_sha256,
        "policy_set_identity": spec.policy_set_identity,
        "data_generation": next(iter(generations)),
        "evaluation_sessions": [item.isoformat() for item in plan.evaluation_sessions],
        "sources": [projections[identity]["source"] for identity in expected_identities],
    }
    publication_id = "challenges-" + hashlib.sha256(canonical_json_bytes(binding)).hexdigest()
    stage_root = (
        Path(output_root).resolve()
        if output_root is not None
        else root / "results" / "workflows" / study.parents[2].name / study.name / CHALLENGE_STAGE
    )
    target = stage_root / publication_id

    artifacts: dict[str, bytes] = {}
    gates: list[dict[str, Any]] = []
    for challenge_id in sorted(REQUIRED_STUDY_TIME_CHALLENGES):
        contract = contracts[challenge_id]
        observed, raw_values = _execute_challenge(
            challenge_id,
            contract=contract,
            projections=projections,
            selected_identity=spec.research_identity,
            baseline_identity=spec.family_baseline_research_identity,
            benchmarks=spec_payload["benchmarks"],
        )
        artifact = {
            "schema_version": 1,
            "kind": "fixed-calendar-challenge-evidence",
            **binding,
            "challenge_id": challenge_id,
            "evidence_identity": contract["evidence_identity"],
            "applies_to": contract["applies_to"],
            "method": contract["method"],
            "metric": contract["gate"]["metric"],
            "observed": observed,
            "raw_values": raw_values,
            "authority": "challenge-only",
        }
        content = canonical_json_bytes(artifact)
        digest = hashlib.sha256(content).hexdigest()
        filename = f"{challenge_id}-{digest}.json"
        artifacts[filename] = content
        relative = target / filename
        gates.append(
            {
                "id": challenge_id,
                "evidence_identity": contract["evidence_identity"],
                "applies_to": contract["applies_to"],
                "gate": contract["gate"],
                "observed": observed,
                "passed": _evaluate_gate(observed, contract["gate"]),
                "evidence": {
                    "path": _relative_or_absolute(relative, root),
                    "sha256": digest,
                },
            }
        )
    manifest = {
        "schema_version": 1,
        "kind": "fixed-calendar-challenge-manifest",
        "study_path": spec.study_identity.study_path,
        "preregistration_sha256": spec.study_identity.preregistration_sha256,
        "qualification_spec_sha256": spec.study_identity.qualification_spec_sha256,
        "development_authorization_sha256": spec.study_identity.development_authorization_sha256,
        "candidate_freeze_sha256": spec.study_identity.candidate_freeze_sha256,
        "qualification_plan_id": plan_id,
        "publication_id": publication_id,
        "gates": gates,
        "authority": "challenge-only",
    }
    artifacts["MANIFEST.json"] = canonical_json_bytes(manifest)
    if dry_run:
        _verify_publication(target, artifacts, allow_missing=True)
        return target / "MANIFEST.json"

    stage_root.mkdir(parents=True, exist_ok=True)
    with locked_file(stage_root / ".challenge-publication.lock", 10.0):
        if target.exists():
            _verify_publication(target, artifacts, allow_missing=False)
            return target / "MANIFEST.json"
        temporary = Path(tempfile.mkdtemp(prefix=".challenge-stage-", dir=stage_root))
        try:
            for filename, content in artifacts.items():
                path = temporary / filename
                path.write_bytes(content)
                with path.open("rb") as handle:
                    os.fsync(handle.fileno())
            os.rename(temporary, target)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return target / "MANIFEST.json"


def _load_projection(
    *,
    root: Path,
    identity: str,
    manifest_path: Path,
    expected_trial_id: str,
    expected_fingerprint: str,
    expected_policy_set: str,
    expected_workflow_path: Path,
    expected_workflow_release_sha256: str,
    evaluation_sessions: tuple[date, ...],
    trial_state: Mapping[str, object],
    research_data_store: ResearchDataStore,
) -> dict[str, Any]:
    manifest_source = _repo_file(root, manifest_path, f"{identity} manifest")
    manifest = research_data_store.load_manifest(manifest_source)
    if manifest.definition is None or manifest.definition.fingerprint != expected_fingerprint:
        raise ValueError(f"{identity} manifest differs from frozen definition")
    try:
        definition_payload = ResearchDefinitionStore(research_data_store.root).load(
            manifest.definition
        )
    except Exception as exc:  # noqa: BLE001 - immutable source boundary fails closed
        raise ValueError(f"{identity} definition blob cannot be verified: {exc}") from exc
    policy_set = definition_payload.get("policy_set")
    if not isinstance(policy_set, dict) or policy_set.get("identity") != expected_policy_set:
        raise ValueError(f"{identity} policy set differs from the frozen study")

    trials = trial_state.get("trials")
    if not isinstance(trials, list):
        raise ValueError("challenge operation requires a verified trial registry")
    matches = [
        item
        for item in trials
        if isinstance(item, dict)
        and item.get("trial_id") == expected_trial_id
        and item.get("definition_fingerprint") == expected_fingerprint
    ]
    if len(matches) != 1:
        raise ValueError(f"{identity} has no unique frozen trial")
    observations = matches[0].get("observations")
    valid = (
        [
            item
            for item in observations
            if isinstance(item, dict)
            and item.get("event") == "observation"
            and item.get("snapshot_id") == manifest.snapshot_id
            and item.get("run_mode") == "offline"
            and item.get("outcome_status") == "succeeded"
            and item.get("validity_status") == "valid"
        ]
        if isinstance(observations, list)
        else []
    )
    if len(valid) != 1 or not isinstance(valid[0].get("result_path"), str):
        raise ValueError(f"{identity} has no unique valid offline Evaluation observation")
    result_path = _resolve_repo_result(root, str(valid[0]["result_path"]))
    result = _json_object(result_path)
    _validate_workflow_provenance(
        result,
        root=root,
        workflow_path=expected_workflow_path,
        workflow_release_sha256=expected_workflow_release_sha256,
        policy_set_identity=expected_policy_set,
    )
    canonical = result.get("canonical_sleeve_evidence")
    error = _canonical_sleeve_evidence_error(canonical)
    if error is not None:
        raise ValueError(f"{identity} result canonical evidence is invalid: {error}")
    if (
        result.get("data_snapshot_id") != manifest.snapshot_id
        or result.get("definition_fingerprint") != expected_fingerprint
        or result.get("run_mode") != "offline"
        or result.get("data_cutoff") != evaluation_sessions[-1].isoformat()
    ):
        raise ValueError(f"{identity} result identity or Evaluation cutoff drifted")
    result_manifest = _resolve_result_manifest(
        root, result_path, result.get("data_snapshot_manifest")
    )
    if result_manifest != manifest_source:
        raise ValueError(f"{identity} result uses a different manifest")
    if not isinstance(canonical, dict):  # pragma: no cover - validator establishes mapping
        raise ValueError(f"{identity} canonical evidence is malformed")
    projection = _project_canonical(canonical, evaluation_sessions)
    data_generation = hashlib.sha256(
        canonical_json_bytes(
            [
                {
                    "series": item.series.storage_key,
                    "role": item.role,
                    "data_cutoff": item.data_cutoff.isoformat(),
                    "blob": item.blob.digest,
                }
                for item in manifest.data
            ]
        )
    ).hexdigest()
    return {
        **projection,
        "data_generation": data_generation,
        "source": {
            "identity": identity,
            "trial_id": expected_trial_id,
            "definition_fingerprint": expected_fingerprint,
            "manifest_path": manifest_source.relative_to(root).as_posix(),
            "manifest_sha256": _sha256(manifest_source),
            "snapshot_id": manifest.snapshot_id,
            "observation_id": valid[0].get("observation_id"),
            "result_path": result_path.relative_to(root).as_posix(),
            "result_sha256": _sha256(result_path),
        },
    }


def _validate_workflow_provenance(
    result: Mapping[str, Any],
    *,
    root: Path,
    workflow_path: Path,
    workflow_release_sha256: str,
    policy_set_identity: str,
) -> None:
    """Reject results produced under any workflow or policy identity drift."""
    metadata = result.get("metadata")
    provenance = metadata.get("observation_provenance") if isinstance(metadata, Mapping) else None
    workflow = provenance.get("workflow") if isinstance(provenance, Mapping) else None
    if not isinstance(workflow, Mapping):
        raise ValueError("challenge result lacks exact workflow observation provenance")
    release_path = Path(workflow_path) / "RELEASE.json"
    definition_path = Path(workflow_path) / "WORKFLOW.md"
    release = _json_object(release_path)
    source_path = workflow.get("path")
    if not isinstance(source_path, str) or not source_path:
        raise ValueError("challenge result workflow path is missing")
    resolved_source = (
        (root / source_path).resolve()
        if not Path(source_path).is_absolute()
        else Path(source_path).resolve()
    )
    expected = {
        "workflow": release.get("workflow"),
        "version": release.get("version"),
        "release_sha256": workflow_release_sha256,
        "workflow_sha256": _sha256(definition_path),
        "policy_set_identity": policy_set_identity,
    }
    if resolved_source != Path(workflow_path).resolve() or any(
        workflow.get(field) != value for field, value in expected.items()
    ):
        raise ValueError("challenge result workflow or policy provenance drifted")


def _project_canonical(canonical: dict[str, Any], sessions: tuple[date, ...]) -> dict[str, Any]:
    session_ids = tuple(item.isoformat() for item in sessions)
    session_set = set(session_ids)
    scenarios: dict[str, Any] = {}
    for name in ("base_net", "stress_net"):
        raw = canonical["scenarios"][name]
        points = [item for item in raw["daily_equity"] if item.get("date") in session_set]
        dates = tuple(str(item.get("date")) for item in points)
        if dates != session_ids:
            raise ValueError(f"challenge source lacks exact ordered {name} Evaluation sessions")
        trades = [
            item
            for item in raw["trades"]
            if item.get("entry_date") in session_set
            and (item.get("exit_date") is None or item.get("exit_date") in session_set)
        ]
        metrics = compute_daily_equity_metrics(
            [float(item["equity"]) for item in points],
            initial_equity=float(canonical["initial_capital"]),
        )
        scenarios[name] = {
            "daily_equity": points,
            "trades": trades,
            "metrics": {
                "total_return": metrics.total_return,
                "max_drawdown": metrics.max_drawdown,
                "profit_factor": _trade_profit_factor(trades),
            },
        }
    candidates = [
        item for item in canonical["raw_candidates"] if item.get("signal_date") in session_set
    ]
    return {
        "evaluation_sessions": list(session_ids),
        "scenarios": scenarios,
        "candidates": candidates,
    }


def _execute_challenge(
    challenge_id: str,
    *,
    contract: dict[str, Any],
    projections: Mapping[str, dict[str, Any]],
    selected_identity: str,
    baseline_identity: str,
    benchmarks: Mapping[str, Any],
) -> tuple[bool, dict[str, Any]]:
    selected = projections[selected_identity]
    targets = [
        projections[item] for item in contract["applies_to"]["identities"] if item in projections
    ]
    base = selected["scenarios"]["base_net"]
    stress = selected["scenarios"]["stress_net"]
    if challenge_id == "cash":
        observed = base["metrics"]["total_return"] > 0
        raw = {"selected_total_return": base["metrics"]["total_return"], "cash_return": 0}
    elif challenge_id == "family-baseline":
        baseline = projections[baseline_identity]["scenarios"]["base_net"]["metrics"][
            "total_return"
        ]
        observed = base["metrics"]["total_return"] > baseline
        raw = {
            "selected_total_return": base["metrics"]["total_return"],
            "baseline_total_return": baseline,
        }
    elif challenge_id == "random-entry":
        returns = _daily_returns(base["daily_equity"])
        samples = _block_bootstrap_returns(
            returns,
            seed=int(benchmarks["random_seed"]),
            repetitions=int(benchmarks["random_samples"]),
            block_sessions=int(benchmarks["bootstrap_block_sessions"]),
        )
        median = sorted(samples)[len(samples) // 2]
        observed = base["metrics"]["total_return"] > median
        raw = {
            "selected_total_return": base["metrics"]["total_return"],
            "bootstrap_returns": samples,
            "median": median,
        }
    elif challenge_id in {"parameter-perturbation", "delayed-entry"}:
        if not targets:
            raise ValueError(f"{challenge_id} method target is outside the frozen family")
        returns = [item["scenarios"]["base_net"]["metrics"]["total_return"] for item in targets]
        observed = all(item > 0 for item in returns)
        raw = {"target_total_returns": returns}
    elif challenge_id in {"higher-costs", "worse-fills"}:
        observed = stress["metrics"]["total_return"] > 0 and _factor_above_one(
            stress["metrics"]["profit_factor"]
        )
        raw = {"stress_metrics": stress["metrics"]}
    elif challenge_id == "missed-entries":
        pnls = [_trade_pnl(item) for item in base["trades"] if item.get("status") == "completed"]
        ordered = list(range(len(pnls)))
        random.Random(int(benchmarks["random_seed"])).shuffle(ordered)
        count = math.floor(len(ordered) * 0.10)
        if count == 0:
            raise ValueError("missed-entries selected zero omissions under the frozen contract")
        dropped = sorted(ordered[:count])
        kept = [value for index, value in enumerate(pnls) if index not in set(dropped)]
        observed = sum(kept) > 0
        raw = {"trade_pnls": pnls, "dropped_indexes": dropped, "kept_pnl": sum(kept)}
    elif challenge_id == "market-regimes":
        quarters = _quarter_returns(base["daily_equity"])
        observed = (
            bool(quarters) and sum(value > 0 for value in quarters.values()) / len(quarters) >= 0.5
        )
        raw = {"calendar_quarter_returns": quarters}
    else:  # pragma: no cover - inventory checked before execution
        raise ValueError(f"unknown challenge implementation: {challenge_id}")
    return bool(observed), raw


def _trial_id(spec: Any, identity: str) -> str:
    if spec.family_trial_ids is None or identity not in spec.family_trial_ids:
        raise ValueError(f"frozen trial id is unavailable for {identity}")
    return str(spec.family_trial_ids[identity])


def _fingerprint(spec: Any, identity: str) -> str:
    freeze = _json_object(spec.study_path / "CANDIDATE_FREEZE.json")
    family = freeze.get("complete_family")
    matches = (
        [
            item
            for item in family
            if isinstance(item, dict) and item.get("source_identity") == identity
        ]
        if isinstance(family, list)
        else []
    )
    if len(matches) != 1 or not isinstance(matches[0].get("definition_fingerprint"), str):
        raise ValueError(f"frozen definition fingerprint is unavailable for {identity}")
    return str(matches[0]["definition_fingerprint"])


def _daily_returns(points: list[dict[str, Any]]) -> list[float]:
    values = [float(item["equity"]) for item in points]
    return [
        0.0 if index == 0 else values[index] / values[index - 1] - 1 for index in range(len(values))
    ]


def _block_bootstrap_returns(
    values: list[float], *, seed: int, repetitions: int, block_sessions: int
) -> list[float]:
    if not values or repetitions <= 0 or block_sessions <= 0:
        raise ValueError("random-entry bootstrap contract is invalid")
    generator = random.Random(seed)
    results: list[float] = []
    for _ in range(repetitions):
        sample: list[float] = []
        while len(sample) < len(values):
            start = generator.randrange(len(values))
            sample.extend(
                values[(start + offset) % len(values)] for offset in range(block_sessions)
            )
        compounded = 1.0
        for value in sample[: len(values)]:
            compounded *= 1 + value
        results.append(compounded - 1)
    return results


def _quarter_returns(points: list[dict[str, Any]]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for point in points:
        session = date.fromisoformat(str(point["date"]))
        grouped.setdefault(f"{session.year}-Q{(session.month - 1) // 3 + 1}", []).append(
            float(point["equity"])
        )
    return {key: values[-1] / values[0] - 1 for key, values in grouped.items() if values}


def _trade_profit_factor(trades: list[dict[str, Any]]) -> str:
    values = [_trade_pnl(item) for item in trades if item.get("status") == "completed"]
    profit = sum(item for item in values if item > 0)
    loss = abs(sum(item for item in values if item < 0))
    if not loss:
        return "Infinity" if profit else "0.0"
    return str(profit / loss)


def _trade_pnl(trade: Mapping[str, Any]) -> float:
    return float(trade["quantity"]) * (
        float(trade["executed_exit_price"]) - float(trade["executed_entry_price"])
    ) - float(trade["total_fees"])


def _factor_above_one(value: object) -> bool:
    return value == "Infinity" or float(str(value)) > 1


def _evaluate_gate(observed: object, gate: Mapping[str, Any]) -> bool:
    operator = gate.get("operator")
    threshold = gate.get("threshold")
    if operator in {"=", "=="}:
        return observed == threshold
    if operator == "!=":
        return observed != threshold
    left = float(str(observed))
    right = float(str(threshold))
    return {">": left > right, ">=": left >= right, "<": left < right, "<=": left <= right}.get(
        str(operator), False
    )


def _resolve_repo_result(root: Path, identity: str) -> Path:
    requested = (
        (root / identity).resolve()
        if not Path(identity).is_absolute()
        else Path(identity).resolve()
    )
    try:
        requested.relative_to(root)
    except ValueError as exc:
        raise ValueError("challenge result path escapes the repository") from exc
    try:
        return resolve_result_path(requested, repository_root=root)
    except ResultPathMigrationError as exc:
        raise ValueError(str(exc)) from exc


def _resolve_result_manifest(root: Path, result_path: Path, value: object) -> Path:
    if not isinstance(value, str):
        raise ValueError("challenge result manifest identity is missing")
    raw = Path(value)
    candidates = [raw, root / raw, result_path.parent / raw]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file():
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            return resolved
    raise ValueError("challenge result manifest cannot be resolved")


def _repo_file(root: Path, path: Path, label: str) -> Path:
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} is outside the repository") from exc
    if not candidate.is_file():
        raise ValueError(f"{label} is missing")
    return candidate


def _json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read challenge evidence {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"challenge evidence must be an object: {path}")
    return payload


def _verify_publication(
    target: Path, artifacts: Mapping[str, bytes], *, allow_missing: bool
) -> None:
    if not target.exists():
        if allow_missing:
            return
        raise ValueError("challenge publication disappeared")
    if not target.is_dir() or {item.name for item in target.iterdir()} != set(artifacts):
        raise ValueError("challenge publication is partial or conflicting")
    if any((target / name).read_bytes() != content for name, content in artifacts.items()):
        raise ValueError("challenge publication collision")


def _relative_or_absolute(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

import hashlib
import json
import subprocess
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from trading.core.accounting import canonical_json_bytes
from trading.core.qualification import (
    HISTORICAL_QUALIFICATION_GATE_NAMES,
    EvaluationEvidenceAudit,
    ExposureMatchedRandomSample,
    HistoricalAggregateEvidence,
    HistoricalBenchmarkEvidence,
    HistoricalFoldEvidence,
    HistoricalScreenResult,
    RetrospectiveSelectionCheckpoint,
    SelectionAdjustmentResult,
    StudyQualificationIdentity,
    build_historical_qualification_plan,
    historical_screen_gates,
)
from trading.core.study_qualification import REQUIRED_STUDY_TIME_CHALLENGES
from trading.core.study_terminal_evidence import validate_study_time_terminal_evidence
from trading.core.workflow_authoring import WorkflowRepository
from trading.research_data import QualificationEvidenceStore, QualificationRegistry


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _development_gate_path(tmp_path: Path) -> Path:
    return tmp_path / "results" / "study-evidence" / "example--s001" / "development-gate.json"


def _development_authorization_sha(study: Path) -> str:
    return _digest(study / "DEVELOPMENT_AUTHORIZATION.json")


def _compound(values: tuple[float, ...]) -> float:
    equity = 1.0
    for value in values:
        equity *= 1.0 + value
    return equity - 1.0


def _applies_to(challenge: str) -> dict:
    if challenge == "cash":
        return {"kind": "benchmark", "identities": ["cash"]}
    if challenge == "family-baseline":
        return {"kind": "trial", "identities": ["baseline-trial"]}
    if challenge == "random-entry":
        return {"kind": "benchmark", "identities": ["random-entry"]}
    return {"kind": "method", "identities": [f"{challenge}-definition"]}


def _passing_fixture(
    tmp_path: Path,
    *,
    include_screen: bool = True,
    plan_trial_registry_identity: str = "state/trials.json",
) -> tuple[Path, Path, Path]:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "example--s001"
    study.mkdir(parents=True)
    relative_study = study.relative_to(tmp_path).as_posix()
    (study / "PLAN.md").write_text("# Frozen plan\n", encoding="utf-8")
    _write_json(study.parents[2] / "RELEASE.json", {"schema_version": 1})
    _write_json(study / "PREREGISTRATION.json", {"schema_version": 1})
    frozen_gate = {"metric": "stress_return", "operator": ">", "threshold": 0}
    _write_json(
        study / "QUALIFICATION_SPEC.json",
        {
            "schema_version": 1,
            "policy_set": {"identity": "9" * 64},
            "evidence_contract": {
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
            },
            "registries": {
                "trial_registry_path": "state/trials.json",
                "qualification_registry_path": "state/qualification.json",
            },
            "required_challenges": [
                {
                    "id": challenge,
                    "evidence_identity": f"{challenge}-evidence",
                    "applies_to": _applies_to(challenge),
                    "gate": frozen_gate,
                }
                for challenge in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
            ],
        },
    )
    _write_json(study / "CANDIDATE_FREEZE.json", {"schema_version": 1})
    _write_json(
        study / "DEVELOPMENT_AUTHORIZATION.json",
        {
            "schema_version": 1,
            "study_path": relative_study,
            "route": "study-time-retrospective",
            "approved_by": "owner@example.com",
        },
    )
    preregistration_sha = _digest(study / "PREREGISTRATION.json")
    spec_sha = _digest(study / "QUALIFICATION_SPEC.json")
    evidence_contract_sha = hashlib.sha256(
        canonical_json_bytes(
            json.loads((study / "QUALIFICATION_SPEC.json").read_text(encoding="utf-8"))[
                "evidence_contract"
            ]
        )
    ).hexdigest()
    freeze_sha = _digest(study / "CANDIDATE_FREEZE.json")
    plan_sha = _digest(study / "PLAN.md")
    release_sha = _digest(study.parents[2] / "RELEASE.json")
    development_authorization_sha = _digest(study / "DEVELOPMENT_AUTHORIZATION.json")

    registry_path = tmp_path / "state" / "qualification.json"
    created_at = datetime(2026, 1, 2, 20, tzinfo=UTC)
    selected_id = "selected-trial"
    baseline_id = "baseline-trial"
    evaluation_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2014-01-01", "2018-12-31")
    )
    development_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2010-01-01", "2012-12-31")
    )
    plan = build_historical_qualification_plan(
        experiment_family="FXI:study-time",
        definition_fingerprint="a" * 64,
        sessions=evaluation_sessions,
        evaluation_years=(2014, 2015, 2016, 2017, 2018),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id=baseline_id,
        random_seed=7,
        random_samples=10,
        bootstrap_repetitions=10,
        bootstrap_block_sessions=5,
        created_at=created_at,
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=created_at,
            selected_trial_id=selected_id,
            included_trial_ids=(baseline_id, selected_id),
            prior_selection_history_incomplete=True,
        ),
        evidence_role="study-time-retrospective",
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=created_at,
            justification="Prior access cannot be excluded.",
            trial_history_complete=False,
        ),
        development_sessions=development_sessions,
        warmup_sessions=tuple(
            timestamp.date() for timestamp in pd.bdate_range("2009-01-01", "2009-12-31")
        ),
        quarantined_sessions=tuple(
            timestamp.date() for timestamp in pd.bdate_range("2013-01-01", "2013-12-31")
        ),
        study_identity=StudyQualificationIdentity(
            study_path=relative_study,
            preregistration_sha256=preregistration_sha,
            plan_sha256=plan_sha,
            candidate_freeze_sha256=freeze_sha,
            qualification_spec_sha256=spec_sha,
            workflow_release_sha256=release_sha,
            development_authorization_sha256=development_authorization_sha,
            operation_approved_by="reviewer@example.com",
            operation_approved_at=created_at,
            contamination_declaration="Historical access cannot be excluded.",
            trial_registry_path=str((tmp_path / "state" / "trials.json").resolve()),
            qualification_registry_path=str(registry_path.resolve()),
            trial_registry_identity=plan_trial_registry_identity,
            qualification_registry_identity="state/qualification.json",
            policy_set_identity="9" * 64,
            evidence_contract_sha256=evidence_contract_sha,
        ),
    )
    plan_id = plan.plan_id
    screen_event_id = f"historical-screen:{plan_id}"
    folds = tuple(
        HistoricalFoldEvidence(
            fold_id=fold.fold_id,
            evaluation_year=fold.evaluation_year,
            signal_count=5,
            candidate_count=5,
            completed_trades=5,
            cumulative_return=0.01,
            stress_cumulative_return=0.005,
            stress_max_drawdown=-0.01,
            gross_profit=2.0,
            gross_loss=1.0,
            stress_gross_profit=1.5,
            stress_gross_loss=1.0,
        )
        for fold in plan.folds
    )
    aggregate = HistoricalAggregateEvidence(
        completed_trades=25,
        traded_folds=5,
        positive_traded_fold_rate=1.0,
        cumulative_return=_compound((0.01,) * 5),
        profit_factor="2.0",
        stress_cumulative_return=_compound((0.005,) * 5),
        stress_profit_factor="1.5",
        stress_max_drawdown=-0.01,
        trade_fold_concentration=0.2,
        profit_fold_concentration=0.2,
    )
    benchmarks = HistoricalBenchmarkEvidence(
        cash_return=0.0,
        family_baseline_return=0.01,
        random_entry_samples=tuple(
            ExposureMatchedRandomSample(
                sample_index=index,
                cumulative_return=0.001,
                completed_trades=25,
                entry_months=(1,) * 25,
                holding_sessions=(1,) * 25,
            )
            for index in range(10)
        ),
    )
    selection_adjustment = SelectionAdjustmentResult(
        selected_trial_id=selected_id,
        included_trial_ids=(baseline_id, selected_id),
        observed_mean_excess_return=Decimal("0.01"),
        adjusted_confidence=Decimal("0.95"),
        repetitions=10,
        block_sessions=5,
        passed=True,
    )
    gates = historical_screen_gates(plan, aggregate, benchmarks, selection_adjustment)
    assert tuple(gate.name for gate in gates) == HISTORICAL_QUALIFICATION_GATE_NAMES
    assert all(gate.passed for gate in gates)
    screen = HistoricalScreenResult(
        plan_id=plan_id,
        folds=folds,
        aggregate=aggregate,
        benchmarks=benchmarks,
        selection_adjustment=selection_adjustment,
        gates=gates,
        passed=True,
        disposition="retrospectively-supported",
    )
    registry = QualificationRegistry(registry_path, now=lambda: created_at)
    registry.register_historical_plan(plan)
    if include_screen:
        registry.record_historical_screen(screen, evaluated_at=datetime(2026, 1, 3, tzinfo=UTC))
    qualification_path, qualification_digest = QualificationEvidenceStore(
        tmp_path / "results" / "qualification-evidence"
    ).publish_registry(
        registry_path,
        repository_root=tmp_path,
        source_registry_identity="state/qualification.json",
    )

    evidence_root = tmp_path / "results" / "study-evidence" / "example--s001"
    challenge_manifest = evidence_root / "challenge-manifest.json"
    _write_json(
        challenge_manifest,
        {
            "study_path": relative_study,
            "preregistration_sha256": preregistration_sha,
            "candidate_freeze_sha256": freeze_sha,
            "qualification_spec_sha256": spec_sha,
            "development_authorization_sha256": development_authorization_sha,
            "qualification_plan_id": plan_id,
            "gates": [
                {
                    "id": challenge,
                    "passed": True,
                    "evidence_identity": f"{challenge}-evidence",
                    "applies_to": _applies_to(challenge),
                    "gate": frozen_gate,
                    "observed": "0.01",
                    "evidence": {
                        "path": (
                            Path("results")
                            / "study-evidence"
                            / "example--s001"
                            / "challenges"
                            / f"{challenge}.json"
                        ).as_posix(),
                        "sha256": "",
                    },
                }
                for challenge in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
            ],
        },
    )
    manifest = json.loads(challenge_manifest.read_text(encoding="utf-8"))
    for gate in manifest["gates"]:
        evidence_path = tmp_path / gate["evidence"]["path"]
        _write_json(
            evidence_path,
            {
                "schema_version": 1,
                "study_path": relative_study,
                "qualification_spec_sha256": spec_sha,
                "candidate_freeze_sha256": freeze_sha,
                "qualification_plan_id": plan_id,
                "challenge_id": gate["id"],
                "evidence_identity": gate["evidence_identity"],
                "applies_to": gate["applies_to"],
                "metric": gate["gate"]["metric"],
                "observed": gate["observed"],
            },
        )
        gate["evidence"]["sha256"] = _digest(evidence_path)
    _write_json(challenge_manifest, manifest)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    _write_json(
        terminal_path,
        {
            "schema_version": 1,
            "study_path": relative_study,
            "route": "study-time-retrospective",
            "decision_stage": "retrospective-evaluation",
            "preregistration_sha256": preregistration_sha,
            "qualification_spec_sha256": spec_sha,
            "development_authorization_sha256": development_authorization_sha,
            "candidate_freeze_sha256": freeze_sha,
            "qualification_evidence": {
                "path": qualification_path.relative_to(tmp_path).as_posix(),
                "sha256": qualification_digest,
                "plan_id": plan_id,
                "screen_event_id": screen_event_id,
            },
            "challenge_manifest": {
                "path": challenge_manifest.relative_to(tmp_path).as_posix(),
                "sha256": _digest(challenge_manifest),
            },
        },
    )
    return study, qualification_path, challenge_manifest


def test_study_time_pass_requires_exact_linked_screen_and_challenges(tmp_path) -> None:
    study, _registry, _challenges = _passing_fixture(tmp_path)

    digest = validate_study_time_terminal_evidence(
        study_path=study,
        outcome="pass",
        disposition="retrospectively-supported",
        decision_stage="retrospective-evaluation",
    )

    assert digest == _digest(study / "TERMINAL_EVIDENCE.json")


def test_study_time_terminal_rejects_lookalike_registry_identity(tmp_path) -> None:
    study, _registry, _challenges = _passing_fixture(
        tmp_path,
        plan_trial_registry_identity="alternate-root/state/trials.json",
    )

    with pytest.raises(ValueError, match="different frozen registry identities"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_terminal_evidence_survives_git_gc_and_fresh_clone(tmp_path) -> None:
    source = tmp_path / "source"
    study, _registry, _challenges = _passing_fixture(source)
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=source, check=True)
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=source, check=True)
    subprocess.run(["git", "gc", "--prune=now"], cwd=source, check=True)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(source), str(clone)], check=True)
    cloned_study = clone / study.relative_to(source)

    validate_study_time_terminal_evidence(
        study_path=cloned_study,
        outcome="pass",
        disposition="retrospectively-supported",
        decision_stage="retrospective-evaluation",
    )


def test_workflow_validator_requires_every_terminal_artifact_in_git_index(tmp_path) -> None:
    study, qualification_path, challenge_manifest = _passing_fixture(tmp_path)
    manifest = json.loads(challenge_manifest.read_text(encoding="utf-8"))
    referenced = {
        qualification_path.resolve(),
        challenge_manifest.resolve(),
        *(tmp_path / gate["evidence"]["path"] for gate in manifest["gates"]),
    }
    indexed: set[Path] = set()
    repository = WorkflowRepository(
        tmp_path / "workflows",
        git_index_checker=lambda path: path.resolve() in indexed,
    )
    metadata = {
        "outcome": "pass",
        "disposition": "retrospectively-supported",
        "decision_stage": "retrospective-evaluation",
    }
    issues = []

    repository._validate_study_time_terminal(metadata, study / "README.md", issues)

    assert len(issues) == len(referenced)
    assert all("not in the Git index" in issue.message for issue in issues)
    indexed.update(path.resolve() for path in referenced)
    issues = []
    repository._validate_study_time_terminal(metadata, study / "README.md", issues)
    assert issues == []


def test_study_time_pass_rejects_non_authoritative_registry_bytes(tmp_path) -> None:
    study, qualification_path, _challenges = _passing_fixture(tmp_path)
    artifact = json.loads(qualification_path.read_text(encoding="utf-8"))
    artifact["registry_json"] += "\n"
    artifact["registry_sha256"] = hashlib.sha256(
        artifact["registry_json"].encode("utf-8")
    ).hexdigest()
    replacement = json.dumps(
        artifact,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    replacement_digest = hashlib.sha256(replacement).hexdigest()
    replacement_path = qualification_path.with_name(f"{replacement_digest}.json")
    replacement_path.write_bytes(replacement)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["qualification_evidence"].update(
        path=replacement_path.relative_to(tmp_path).as_posix(),
        sha256=replacement_digest,
    )
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="cannot be replayed"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_forged_hash_consistent_incomplete_screen(tmp_path) -> None:
    study, qualification_path, _challenges = _passing_fixture(tmp_path)
    outer = json.loads(qualification_path.read_text(encoding="utf-8"))
    registry = json.loads(outer["registry_json"])
    screen_event = next(
        event for event in registry["events"] if event["event_type"] == "historical_screen"
    )
    screen_event["payload"]["gates"] = screen_event["payload"]["gates"][:1]
    previous_hash = "0" * 64
    for event in registry["events"]:
        event["previous_hash"] = previous_hash
        content = {
            "sequence": event["sequence"],
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "payload": event["payload"],
            "previous_hash": previous_hash,
        }
        event["event_hash"] = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        previous_hash = event["event_hash"]
    registry_bytes = canonical_json_bytes(registry)
    checkpoint_bytes = canonical_json_bytes(
        {
            "schema_version": 1,
            "event_count": len(registry["events"]),
            "registry_checksum": hashlib.sha256(registry_bytes).hexdigest(),
            "head_hash": previous_hash,
        }
    )
    outer.update(
        registry_json=registry_bytes.decode("utf-8"),
        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
        checkpoint_json=checkpoint_bytes.decode("utf-8"),
        checkpoint_sha256=hashlib.sha256(checkpoint_bytes).hexdigest(),
    )
    replacement = canonical_json_bytes(outer)
    replacement_digest = hashlib.sha256(replacement).hexdigest()
    replacement_path = qualification_path.with_name(f"{replacement_digest}.json")
    replacement_path.write_bytes(replacement)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["qualification_evidence"].update(
        path=replacement_path.relative_to(tmp_path).as_posix(),
        sha256=replacement_digest,
    )
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="gates do not reproduce frozen evidence"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_forged_duplicate_screen_event(tmp_path) -> None:
    study, qualification_path, _challenges = _passing_fixture(tmp_path)
    outer = json.loads(qualification_path.read_text(encoding="utf-8"))
    registry = json.loads(outer["registry_json"])
    screen_event = next(
        event for event in registry["events"] if event["event_type"] == "historical_screen"
    )
    forged = deepcopy(screen_event)
    forged["sequence"] = len(registry["events"]) + 1
    forged["event_id"] = f"forged-screen:{forged['payload']['plan_id']}"
    registry["events"].append(forged)
    previous_hash = "0" * 64
    for event in registry["events"]:
        event["previous_hash"] = previous_hash
        content = {
            "sequence": event["sequence"],
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "payload": event["payload"],
            "previous_hash": previous_hash,
        }
        event["event_hash"] = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        previous_hash = event["event_hash"]
    registry_bytes = canonical_json_bytes(registry)
    checkpoint_bytes = canonical_json_bytes(
        {
            "schema_version": 1,
            "event_count": len(registry["events"]),
            "registry_checksum": hashlib.sha256(registry_bytes).hexdigest(),
            "head_hash": previous_hash,
        }
    )
    outer.update(
        registry_json=registry_bytes.decode("utf-8"),
        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
        checkpoint_json=checkpoint_bytes.decode("utf-8"),
        checkpoint_sha256=hashlib.sha256(checkpoint_bytes).hexdigest(),
    )
    replacement = canonical_json_bytes(outer)
    replacement_digest = hashlib.sha256(replacement).hexdigest()
    replacement_path = qualification_path.with_name(f"{replacement_digest}.json")
    replacement_path.write_bytes(replacement)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["qualification_evidence"].update(
        path=replacement_path.relative_to(tmp_path).as_posix(),
        sha256=replacement_digest,
        screen_event_id=forged["event_id"],
    )
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="cannot be replayed.*screen"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_missing_screen(tmp_path) -> None:
    study, _registry_path, _challenges = _passing_fixture(tmp_path, include_screen=False)

    with pytest.raises(ValueError, match="no exact linked plan and screen"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_missing_required_challenge(tmp_path) -> None:
    study, _registry, challenge_manifest = _passing_fixture(tmp_path)
    manifest = json.loads(challenge_manifest.read_text(encoding="utf-8"))
    manifest["gates"] = manifest["gates"][:-1]
    _write_json(challenge_manifest, manifest)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["challenge_manifest"]["sha256"] = _digest(challenge_manifest)
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="missing a required challenge"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_duplicate_required_challenge(tmp_path) -> None:
    study, _registry, challenge_manifest = _passing_fixture(tmp_path)
    manifest = json.loads(challenge_manifest.read_text(encoding="utf-8"))
    manifest["gates"].append(dict(manifest["gates"][0]))
    _write_json(challenge_manifest, manifest)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["challenge_manifest"]["sha256"] = _digest(challenge_manifest)
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="missing a required challenge"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


@pytest.mark.parametrize("artifact", ["PLAN.md", "RELEASE.json"])
def test_study_time_pass_rejects_plan_or_release_drift(tmp_path, artifact: str) -> None:
    study, _registry, _challenges = _passing_fixture(tmp_path)
    path = study / artifact if artifact == "PLAN.md" else study.parents[2] / artifact
    path.write_bytes(path.read_bytes() + b"drift\n")

    with pytest.raises(ValueError, match="different frozen study"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_study_time_pass_rejects_manifest_observed_not_supported_by_artifact(tmp_path) -> None:
    study, _registry, challenge_manifest = _passing_fixture(tmp_path)
    manifest = json.loads(challenge_manifest.read_text(encoding="utf-8"))
    gate = manifest["gates"][0]
    evidence_path = tmp_path / gate["evidence"]["path"]
    artifact = json.loads(evidence_path.read_text(encoding="utf-8"))
    artifact["observed"] = "-1"
    _write_json(evidence_path, artifact)
    gate["evidence"]["sha256"] = _digest(evidence_path)
    _write_json(challenge_manifest, manifest)
    terminal_path = study / "TERMINAL_EVIDENCE.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["challenge_manifest"]["sha256"] = _digest(challenge_manifest)
    _write_json(terminal_path, terminal)

    with pytest.raises(ValueError, match="observed value lacks evidence"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="pass",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
        )


def test_development_failure_rejects_existing_candidate_freeze(tmp_path) -> None:
    study, _registry, _challenges = _passing_fixture(tmp_path)
    relative_study = study.relative_to(tmp_path).as_posix()
    development_gate = _development_gate_path(tmp_path)
    _write_json(
        development_gate,
        {
            "study_path": relative_study,
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "complete": True,
            "trustworthy": True,
            "eligible_candidate": None,
            "disposition": "development-selection-failed",
            "trial_budget_exhausted": True,
        },
    )
    _write_json(
        study / "TERMINAL_EVIDENCE.json",
        {
            "schema_version": 1,
            "study_path": relative_study,
            "route": "study-time-retrospective",
            "decision_stage": "development",
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "development_gate": {
                "path": development_gate.relative_to(tmp_path).as_posix(),
                "sha256": _digest(development_gate),
            },
        },
    )

    with pytest.raises(ValueError, match="cannot follow an existing candidate freeze"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="fail",
            disposition="development-selection-failed",
            decision_stage="development",
        )


def test_development_failure_rejects_prior_plan_after_freeze_deleted(tmp_path) -> None:
    study, qualification_path, _challenges = _passing_fixture(tmp_path)
    (study / "CANDIDATE_FREEZE.json").unlink()
    relative_study = study.relative_to(tmp_path).as_posix()
    development_gate = _development_gate_path(tmp_path)
    _write_json(
        development_gate,
        {
            "study_path": relative_study,
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "complete": True,
            "trustworthy": True,
            "eligible_candidate": None,
            "disposition": "development-selection-failed",
            "trial_budget_exhausted": True,
        },
    )
    _write_json(
        study / "TERMINAL_EVIDENCE.json",
        {
            "schema_version": 1,
            "study_path": relative_study,
            "route": "study-time-retrospective",
            "decision_stage": "development",
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "development_gate": {
                "path": development_gate.relative_to(tmp_path).as_posix(),
                "sha256": _digest(development_gate),
            },
            "qualification_absence_evidence": {
                "path": qualification_path.relative_to(tmp_path).as_posix(),
                "sha256": qualification_path.stem,
            },
        },
    )

    with pytest.raises(ValueError, match="cannot follow a qualification plan or screen"):
        validate_study_time_terminal_evidence(
            study_path=study,
            outcome="fail",
            disposition="development-selection-failed",
            decision_stage="development",
            require_current_registry=True,
        )


def _development_failure_fixture(tmp_path: Path) -> Path:
    study, _qualification_path, _challenges = _passing_fixture(tmp_path)
    (study / "CANDIDATE_FREEZE.json").unlink()
    registry_path = tmp_path / "state" / "qualification.json"
    registry_path.unlink()
    registry_path.with_name(f".{registry_path.name}.head.json").unlink()
    qualification_path, qualification_digest = QualificationEvidenceStore(
        tmp_path / "results" / "qualification-evidence"
    ).publish_registry(
        registry_path,
        repository_root=tmp_path,
        source_registry_identity="state/qualification.json",
    )
    relative_study = study.relative_to(tmp_path).as_posix()
    development_gate = _development_gate_path(tmp_path)
    _write_json(
        development_gate,
        {
            "study_path": relative_study,
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "complete": True,
            "trustworthy": True,
            "eligible_candidate": None,
            "disposition": "development-selection-failed",
            "trial_budget_exhausted": True,
        },
    )
    _write_json(
        study / "TERMINAL_EVIDENCE.json",
        {
            "schema_version": 1,
            "study_path": relative_study,
            "route": "study-time-retrospective",
            "decision_stage": "development",
            "preregistration_sha256": _digest(study / "PREREGISTRATION.json"),
            "qualification_spec_sha256": _digest(study / "QUALIFICATION_SPEC.json"),
            "development_authorization_sha256": _development_authorization_sha(study),
            "development_gate": {
                "path": development_gate.relative_to(tmp_path).as_posix(),
                "sha256": _digest(development_gate),
            },
            "qualification_absence_evidence": {
                "path": qualification_path.relative_to(tmp_path).as_posix(),
                "sha256": qualification_digest,
            },
        },
    )

    return study


def test_development_failure_accepts_current_authoritative_absence_snapshot(tmp_path) -> None:
    study = _development_failure_fixture(tmp_path)

    validate_study_time_terminal_evidence(
        study_path=study,
        outcome="fail",
        disposition="development-selection-failed",
        decision_stage="development",
        require_current_registry=True,
    )


def test_development_failure_terminal_survives_git_gc_and_fresh_clone(tmp_path) -> None:
    source = tmp_path / "source"
    study = _development_failure_fixture(source)
    registry_path = source / "state" / "qualification.json"
    registry_path.unlink()
    registry_path.with_name(f".{registry_path.name}.head.json").unlink()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=source, check=True)
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=source, check=True)
    subprocess.run(["git", "gc", "--prune=now"], cwd=source, check=True)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(source), str(clone)], check=True)
    cloned_study = clone / study.relative_to(source)
    repository = WorkflowRepository(clone / "workflows")
    issues = []

    repository._validate_study_time_terminal(
        {
            "outcome": "fail",
            "disposition": "development-selection-failed",
            "decision_stage": "development",
        },
        cloned_study / "README.md",
        issues,
    )

    assert issues == []

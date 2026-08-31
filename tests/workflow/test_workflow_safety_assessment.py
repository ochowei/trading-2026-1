import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import main
from trading.workflow.authoring import (
    ClearSafetyAssessmentRequest,
    MarkdownDocument,
    OpenSafetyAssessmentRequest,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)
from trading.workflow.studies import WorkflowStudyService

FIXED_TIME = datetime(2026, 8, 30, 6, 7, 8, tzinfo=UTC)


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _register_version(
    root: Path,
    *,
    version: str,
    supersedes: str | None,
    status: str = "draft",
    source_changes: list[str] | None = None,
) -> Path:
    registry_path = root / "README.md"
    document = read_markdown_document(registry_path)
    metadata = copy.deepcopy(document.metadata)
    metadata["workflows"]["example-workflow"]["versions"][version] = {
        "path": f"example-workflow--{version}",
        "status": status,
    }
    _write_document(registry_path, metadata, document.body)
    version_path = root / f"example-workflow--{version}"
    _write_document(
        version_path / "README.md",
        {
            "workflow": "example-workflow",
            "title": "Example Workflow",
            "version": version,
            "definition": "WORKFLOW.md",
            "supersedes": supersedes,
            "derived_from": None,
            "source_changes": source_changes or [],
            "capabilities": ["workflow-release-safety-v1"],
            "dependencies": [],
        },
        """# Example Workflow

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
""",
    )
    (version_path / "WORKFLOW.md").write_text(
        """# Example Workflow

## Purpose and decision

Determine whether guarded work may proceed.

## Scope and non-goals

This fixture does not authorize trading.
""",
        encoding="utf-8",
    )
    return version_path


def _accepted_change(tmp_path: Path, predecessor: Path) -> Path:
    change = predecessor / "work" / "changes" / "safety-contract--c001"
    _write_document(
        change / "README.md",
        {
            "id": "C001",
            "title": "Safety contract",
            "workflow": "example-workflow",
            "source_version": "v001",
            "status": "accepted",
            "created_at": "2026-08-30",
            "status_changed_at": "2026-08-30T06:07:08.000000Z",
            "decided_at": "2026-08-30T06:07:08.000000Z",
            "decided_by": "owner@example.com",
            "released_in": None,
        },
        "# Safety contract\n",
    )
    for filename in ("PROPOSAL.md", "IMPACT.md", "VALIDATION.md", "DECISION.md"):
        (change / filename).write_text(
            f"# {filename}\n\nComplete safety-assessment contract for this test.\n",
            encoding="utf-8",
        )
    return change


def _initialize_pair(tmp_path: Path) -> tuple[Path, WorkflowRepository, Path, Path, Path]:
    root = tmp_path / "workflows"
    _write_document(
        root / "README.md",
        {
            "schema_version": 1,
            "workflows": {
                "example-workflow": {
                    "title": "Example Workflow",
                    "activation_required_from": "v002",
                    "versions": {},
                }
            },
        },
        """# Research Workflows

<!-- GENERATED:WORKFLOW_INDEX_START -->
_No workflow versions registered._
<!-- GENERATED:WORKFLOW_INDEX_END -->
""",
    )
    repository = WorkflowRepository(root, now=lambda: FIXED_TIME)
    predecessor = _register_version(root, version="v001", supersedes=None)
    repository.sync()
    repository.release(predecessor, approved_by="owner@example.com")
    repository.attest_activation(
        predecessor,
        approved_by="owner@example.com",
        activation_required_from="v002",
    )
    change = _accepted_change(tmp_path, predecessor)
    successor = _register_version(
        root,
        version="v002",
        supersedes="v001",
        source_changes=[str(change.relative_to(tmp_path))],
    )
    repository.sync()
    study = WorkflowStudyService(root, now=lambda: FIXED_TIME).initialize(
        predecessor,
        study_slug="blocking-study",
        title="Blocking study",
        created_by="operator@example.com",
    )
    return root, repository, predecessor, successor, study


def _open_request(tmp_path: Path, study: Path) -> OpenSafetyAssessmentRequest:
    request = tmp_path / "assessment-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "reason": "release boundary needs an explicit study decision",
                "blocking_studies": [str(study.relative_to(tmp_path))],
                "missing_impact_decisions": [str(study.relative_to(tmp_path))],
            }
        ),
        encoding="utf-8",
    )
    return OpenSafetyAssessmentRequest.from_path(request)


def _clear_request(
    tmp_path: Path,
    study: Path,
    *,
    disposition: str,
    evidence: list[Path] | None = None,
) -> ClearSafetyAssessmentRequest:
    request = tmp_path / "clearance-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "resolutions": [
                    {
                        "study_path": str(study.relative_to(tmp_path)),
                        "disposition": disposition,
                        "evidence": [
                            str(path.relative_to(tmp_path))
                            for path in (evidence or [study / "README.md"])
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return ClearSafetyAssessmentRequest.from_path(request)


def test_guarded_safety_assessment_blocks_new_work_and_release(tmp_path: Path) -> None:
    _root, repository, predecessor, successor, study = _initialize_pair(tmp_path)

    assessment = repository.open_safety_assessment(
        successor,
        _open_request(tmp_path, study),
        opened_by="operator@example.com",
    )

    assessment_path = successor / "work" / "release-safety" / "sa001" / "ASSESSMENT.json"
    assert json.loads(assessment_path.read_text(encoding="utf-8")) == assessment
    assert assessment["assessment_id"] == "SA001"
    assert assessment["predecessor_version"] == "v001"
    assert assessment["successor_version"] == "v002"
    assert (
        assessment["successor_workflow_sha256"]
        == hashlib.sha256((successor / "WORKFLOW.md").read_bytes()).hexdigest()
    )
    assert repository.validate_all() == ()

    with pytest.raises(WorkflowAuthoringError, match="open safety assessment"):
        repository.require_effective_version(predecessor)
    with pytest.raises(WorkflowAuthoringError, match="open safety assessment"):
        WorkflowStudyService(_root, now=lambda: FIXED_TIME).initialize(
            predecessor,
            study_slug="blocked-by-safety",
            title="Blocked by safety",
            created_by="operator@example.com",
        )
    with pytest.raises(WorkflowAuthoringError, match="already has an open"):
        repository.open_safety_assessment(
            successor,
            _open_request(tmp_path, study),
            opened_by="operator@example.com",
        )
    with pytest.raises(WorkflowAuthoringError, match="clear the open safety assessment"):
        repository.release(successor, approved_by="owner@example.com")


def test_clearance_requires_safe_study_then_restores_family_eligibility(tmp_path: Path) -> None:
    root, repository, predecessor, successor, study = _initialize_pair(tmp_path)
    request = _open_request(tmp_path, study)
    repository.open_safety_assessment(
        successor,
        request,
        opened_by="operator@example.com",
    )
    assessment_dir = successor / "work" / "release-safety" / "sa001"

    with pytest.raises(WorkflowAuthoringError, match="not safely paused or terminal"):
        repository.clear_safety_assessment(
            assessment_dir,
            _clear_request(tmp_path, study, disposition="resolved-terminal"),
            approved_by="owner@example.com",
        )

    WorkflowStudyService(root, now=lambda: FIXED_TIME).transition(
        study,
        "cancelled",
        actor="operator@example.com",
        reason="close before workflow replacement",
    )
    clearance = repository.clear_safety_assessment(
        assessment_dir,
        _clear_request(tmp_path, study, disposition="resolved-terminal"),
        approved_by="owner@example.com",
    )

    assert (
        clearance["assessment_sha256"]
        == hashlib.sha256((assessment_dir / "ASSESSMENT.json").read_bytes()).hexdigest()
    )
    assert clearance["resolutions"][0]["status_at_clear"] == "cancelled"
    assert repository.validate_all() == ()
    repository.require_effective_version(predecessor)
    repository.release(successor, approved_by="owner@example.com")
    assert repository.validate_all() == ()


def test_validator_rejects_tampered_safety_evidence(tmp_path: Path) -> None:
    root, repository, _predecessor, successor, study = _initialize_pair(tmp_path)
    repository.open_safety_assessment(
        successor,
        _open_request(tmp_path, study),
        opened_by="operator@example.com",
    )
    WorkflowStudyService(root, now=lambda: FIXED_TIME).transition(
        study,
        "cancelled",
        actor="operator@example.com",
        reason="close before workflow replacement",
    )
    assessment_dir = successor / "work" / "release-safety" / "sa001"
    repository.clear_safety_assessment(
        assessment_dir,
        _clear_request(tmp_path, study, disposition="resolved-terminal"),
        approved_by="owner@example.com",
    )

    clearance_path = assessment_dir / "CLEARANCE.json"
    clearance = json.loads(clearance_path.read_text(encoding="utf-8"))
    clearance["assessment_sha256"] = "0" * 64
    clearance_path.write_text(json.dumps(clearance), encoding="utf-8")

    issues = repository.validate_all()
    assert any("assessment digest does not match" in issue.message for issue in issues)


def test_paused_missing_impact_decision_requires_source_change_evidence(
    tmp_path: Path,
) -> None:
    root, repository, _predecessor, successor, study = _initialize_pair(tmp_path)
    (study / "HYPOTHESIS.md").write_text(
        "# Hypothesis\n\nA fixed hypothesis with a falsifiable result.\n",
        encoding="utf-8",
    )
    (study / "PLAN.md").write_text(
        "# Plan\n\nRun the frozen test without changing its design.\n",
        encoding="utf-8",
    )
    service = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    service.preregister(study, approved_by="owner@example.com")
    service.transition(study, "running", actor="operator@example.com")
    service.transition(
        study,
        "paused",
        actor="operator@example.com",
        reason="workflow replacement review",
    )
    repository.open_safety_assessment(
        successor,
        _open_request(tmp_path, study),
        opened_by="operator@example.com",
    )
    assessment_dir = successor / "work" / "release-safety" / "sa001"

    with pytest.raises(WorkflowAuthoringError, match="source change IMPACT.md"):
        repository.clear_safety_assessment(
            assessment_dir,
            _clear_request(tmp_path, study, disposition="continue-on-v001"),
            approved_by="owner@example.com",
        )

    impact = (
        root / "example-workflow--v001" / "work" / "changes" / "safety-contract--c001" / "IMPACT.md"
    )
    repository.clear_safety_assessment(
        assessment_dir,
        _clear_request(
            tmp_path,
            study,
            disposition="continue-on-v001",
            evidence=[impact],
        ),
        approved_by="owner@example.com",
    )
    assert repository.validate_all() == ()


def test_safety_cli_writes_the_guarded_assessment(tmp_path: Path, capsys) -> None:
    root, _repository, _predecessor, successor, study = _initialize_pair(tmp_path)
    request = tmp_path / "assessment-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "reason": "release boundary needs an explicit study decision",
                "blocking_studies": [str(study.relative_to(tmp_path))],
                "missing_impact_decisions": [],
            }
        ),
        encoding="utf-8",
    )

    main(
        [
            "workflow",
            "--root",
            str(root),
            "safety",
            "assess",
            str(successor),
            "--request",
            str(request),
            "--by",
            "operator@example.com",
        ]
    )

    assert "workflow safety assessment opened: SA001" in capsys.readouterr().out
    WorkflowStudyService(root, now=lambda: FIXED_TIME).transition(
        study,
        "cancelled",
        actor="operator@example.com",
        reason="close before workflow replacement",
    )
    clearance_request = tmp_path / "clearance-request.json"
    clearance_request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "resolutions": [
                    {
                        "study_path": str(study.relative_to(tmp_path)),
                        "disposition": "resolved-terminal",
                        "evidence": [str((study / "README.md").relative_to(tmp_path))],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    main(
        [
            "workflow",
            "--root",
            str(root),
            "safety",
            "clear",
            str(successor / "work" / "release-safety" / "sa001"),
            "--request",
            str(clearance_request),
            "--approved-by",
            "owner@example.com",
        ]
    )
    assert "workflow safety assessment cleared: SA001" in capsys.readouterr().out

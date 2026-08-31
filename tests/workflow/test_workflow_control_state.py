import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import main
from trading.workflow.authoring import (
    MarkdownDocument,
    OpenSafetyAssessmentRequest,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)
from trading.workflow.control_state import evaluate_workflow_control_state
from trading.workflow.studies import WorkflowStudyService

FIXED_TIME = datetime(2026, 8, 31, 8, 30, tzinfo=UTC)
SAFETY_CAPABILITY = "workflow-release-safety-v1"


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _initialize_root(tmp_path: Path) -> tuple[Path, WorkflowRepository]:
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
    return root, WorkflowRepository(root, now=lambda: FIXED_TIME)


def _register_version(
    root: Path,
    *,
    version: str,
    supersedes: str | None,
    capabilities: tuple[str, ...] = (),
    source_changes: tuple[str, ...] = (),
) -> Path:
    registry_path = root / "README.md"
    document = read_markdown_document(registry_path)
    metadata = copy.deepcopy(document.metadata)
    metadata["workflows"]["example-workflow"]["versions"][version] = {
        "path": f"example-workflow--{version}",
        "status": "draft",
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
            "source_changes": list(source_changes),
            "capabilities": list(capabilities),
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

Determine whether a fixed research decision may proceed.

## Scope and non-goals

This fixture does not authorize trading.
""",
        encoding="utf-8",
    )
    return version_path


def _accepted_change(tmp_path: Path, predecessor: Path) -> Path:
    change = predecessor / "work" / "changes" / "control-state--c001"
    _write_document(
        change / "README.md",
        {
            "id": "C001",
            "title": "Control state",
            "workflow": "example-workflow",
            "source_version": "v001",
            "status": "accepted",
            "created_at": "2026-08-31",
            "status_changed_at": "2026-08-31T08:30:00.000000Z",
            "decided_at": "2026-08-31T08:30:00.000000Z",
            "decided_by": "owner@example.com",
            "released_in": None,
        },
        "# Control state\n",
    )
    for filename in ("PROPOSAL.md", "IMPACT.md", "VALIDATION.md", "DECISION.md"):
        (change / filename).write_text(
            f"# {filename}\n\nComplete control-state fixture material for this test.\n",
            encoding="utf-8",
        )
    return change


def _initialize_pair(
    tmp_path: Path,
    *,
    predecessor_capabilities: tuple[str, ...] = (SAFETY_CAPABILITY,),
) -> tuple[Path, WorkflowRepository, Path, Path]:
    root, repository = _initialize_root(tmp_path)
    predecessor = _register_version(
        root,
        version="v001",
        supersedes=None,
        capabilities=predecessor_capabilities,
    )
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
        capabilities=(SAFETY_CAPABILITY,),
        source_changes=(str(change.relative_to(tmp_path)),),
    )
    repository.sync()
    return root, repository, predecessor, successor


def test_exact_version_states_cover_n02_n04_n05_and_n06(tmp_path: Path) -> None:
    root, repository, predecessor, successor = _initialize_pair(tmp_path)

    draft = evaluate_workflow_control_state(repository, successor)
    active_without_studies = evaluate_workflow_control_state(repository, predecessor)

    assert (draft.result, draft.control_state) == ("determined", "N02")
    assert (active_without_studies.result, active_without_studies.control_state) == (
        "determined",
        "N04",
    )
    assert active_without_studies.unfinished_study_count == 0

    study = WorkflowStudyService(root, now=lambda: FIXED_TIME).initialize(
        predecessor,
        study_slug="blocking-study",
        title="Blocking study",
        created_by="operator@example.com",
    )
    active_with_study = evaluate_workflow_control_state(repository, predecessor)

    assert (active_with_study.result, active_with_study.control_state) == (
        "determined",
        "N05",
    )
    assert active_with_study.unfinished_study_count == 1

    repository.open_safety_assessment(
        successor,
        OpenSafetyAssessmentRequest(
            reason="release boundary requires explicit safety evidence",
            blocking_studies=(str(study.relative_to(tmp_path)),),
            missing_impact_decisions=(),
        ),
        opened_by="operator@example.com",
    )
    safety = evaluate_workflow_control_state(repository, predecessor)

    assert (safety.result, safety.control_state) == ("determined", "N06")
    assert safety.safety_assessment is not None


def test_prepared_successor_is_n03_and_superseded_version_is_outside_scope(
    tmp_path: Path,
) -> None:
    _root, repository, predecessor, successor = _initialize_pair(tmp_path)

    repository.release(successor, approved_by="owner@example.com")
    prepared = evaluate_workflow_control_state(repository, successor)

    assert (prepared.result, prepared.control_state) == ("determined", "N03")

    repository.activate(successor, approved_by="owner@example.com")
    superseded = evaluate_workflow_control_state(repository, predecessor)

    assert superseded.result == "outside-a1-2"
    assert superseded.control_state is None
    assert superseded.registry_status == "superseded"


def test_active_version_without_safety_capability_is_indeterminate(tmp_path: Path) -> None:
    _root, repository, predecessor, _successor = _initialize_pair(
        tmp_path,
        predecessor_capabilities=(),
    )

    result = evaluate_workflow_control_state(repository, predecessor)

    assert result.result == "indeterminate"
    assert result.control_state is None
    assert result.reasons == ("safety-capability-unavailable",)


def test_conflicting_persisted_evidence_is_invalid(tmp_path: Path) -> None:
    _root, repository, _predecessor, successor = _initialize_pair(tmp_path)
    (successor / "RELEASE.json").write_text("{}\n", encoding="utf-8")

    result = evaluate_workflow_control_state(repository, successor)

    assert result.result == "invalid"
    assert result.control_state is None
    assert any("draft version must not have RELEASE.json" in issue for issue in result.issues)


def test_control_state_cli_supports_machine_readable_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, _repository, _predecessor, successor = _initialize_pair(tmp_path)

    main(
        [
            "workflow",
            "--root",
            str(root),
            "version",
            "state",
            str(successor),
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "schema_version": 1,
        "workflow": "example-workflow",
        "version": "v002",
        "path": str(successor.relative_to(tmp_path)),
        "result": "determined",
        "control_state": "N02",
        "registry_status": "draft",
        "unfinished_study_count": None,
        "safety_assessment": None,
        "reasons": ["registered-draft"],
        "issues": [],
    }


def test_control_state_cli_exits_nonzero_for_indeterminate_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, _repository, predecessor, _successor = _initialize_pair(
        tmp_path,
        predecessor_capabilities=(),
    )

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "workflow",
                "--root",
                str(root),
                "version",
                "state",
                str(predecessor),
                "--json",
            ]
        )

    assert exc_info.value.code == 2
    assert json.loads(capsys.readouterr().out)["result"] == "indeterminate"

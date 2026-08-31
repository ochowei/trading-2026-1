import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.research_definitions.execution import (
    WorkflowNativeExecutionError,
    resolve_workflow_policy_set,
)
from trading.workflow.authoring import (
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)
from trading.workflow.studies import WorkflowStudyService

FIXED_TIME = datetime(2026, 8, 28, 8, 30, tzinfo=UTC)


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _initialize_root(
    tmp_path: Path,
    *,
    activation_required_from: str | None = "v002",
) -> tuple[Path, WorkflowRepository]:
    root = tmp_path / "workflows"
    _write_document(
        root / "README.md",
        {
            "schema_version": 1,
            "workflows": {
                "example-workflow": {
                    "title": "Example Workflow",
                    **(
                        {"activation_required_from": activation_required_from}
                        if activation_required_from is not None
                        else {}
                    ),
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
    source_changes: list[str] | None = None,
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
            "source_changes": source_changes or [],
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


def _accepted_change(v1: Path, tmp_path: Path) -> Path:
    change = v1 / "work" / "changes" / "explicit-activation--c001"
    _write_document(
        change / "README.md",
        {
            "id": "C001",
            "title": "Explicit activation",
            "workflow": "example-workflow",
            "source_version": "v001",
            "status": "accepted",
            "created_at": "2026-08-28",
            "status_changed_at": "2026-08-28T08:30:00.000000Z",
            "decided_at": "2026-08-28T08:30:00.000000Z",
            "decided_by": "owner@example.com",
            "released_in": None,
        },
        "# Explicit activation\n",
    )
    for name in ("PROPOSAL.md", "IMPACT.md", "VALIDATION.md", "DECISION.md"):
        (change / name).write_text(
            f"# {name}\n\nComplete workflow release activation evidence for this test.\n",
            encoding="utf-8",
        )
    return change


def test_release_prepares_then_activation_atomically_changes_authority(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path)
    v1 = _register_version(root, version="v001", supersedes=None)
    repository.sync()
    repository.release(v1, approved_by="owner@example.com")
    repository.attest_activation(v1, approved_by="owner@example.com")
    change = _accepted_change(v1, tmp_path)
    repository.sync()
    v2 = _register_version(
        root,
        version="v002",
        supersedes="v001",
        source_changes=[str(change.relative_to(tmp_path))],
    )
    repository.sync()

    release = repository.release(v2, approved_by="owner@example.com")

    versions = read_markdown_document(root / "README.md").metadata["workflows"]["example-workflow"][
        "versions"
    ]
    assert versions["v001"]["status"] == "active"
    assert versions["v002"]["status"] == "prepared"
    assert read_markdown_document(change / "README.md").metadata["status"] == "accepted"
    assert not (v2 / "ACTIVATION.json").exists()
    assert release["workflow"] == "example-workflow"
    with pytest.raises(WorkflowNativeExecutionError, match="not active"):
        resolve_workflow_policy_set(v2)
    with pytest.raises(WorkflowAuthoringError, match="prepared successor"):
        WorkflowStudyService(root, now=lambda: FIXED_TIME).initialize(
            v1,
            study_slug="blocked",
            title="Blocked",
            created_by="agent@example.com",
        )

    activation = repository.activate(v2, approved_by="owner@example.com")

    versions = read_markdown_document(root / "README.md").metadata["workflows"]["example-workflow"][
        "versions"
    ]
    assert versions["v001"]["status"] == "superseded"
    assert versions["v002"]["status"] == "active"
    assert (
        versions["v002"]["activation_sha256"]
        == hashlib.sha256((v2 / "ACTIVATION.json").read_bytes()).hexdigest()
    )
    assert activation["basis"] == "explicit-workflow-release-activation"
    assert (
        activation["release_sha256"]
        == hashlib.sha256((v2 / "RELEASE.json").read_bytes()).hexdigest()
    )
    assert read_markdown_document(change / "README.md").metadata["status"] == "released"
    assert repository.validate_all() == ()
    with pytest.raises(WorkflowAuthoringError, match="only a prepared"):
        repository.activate(v2, approved_by="owner@example.com")


def test_activation_evidence_is_required_and_immutable(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path, activation_required_from=None)
    v1 = _register_version(root, version="v001", supersedes=None)
    repository.sync()
    repository.release(v1, approved_by="owner@example.com")

    migration = repository.attest_activation(
        v1,
        approved_by="owner@example.com",
        activation_required_from="v002",
    )

    assert migration["basis"] == "grandfathered-effective-release"
    family = read_markdown_document(root / "README.md").metadata["workflows"]["example-workflow"]
    assert family["activation_required_from"] == "v002"
    assert repository.validate_all() == ()
    with pytest.raises(WorkflowAuthoringError, match="already has ACTIVATION.json"):
        repository.attest_activation(v1, approved_by="owner@example.com")
    (v1 / "ACTIVATION.json").write_text(json.dumps(migration), encoding="utf-8")
    issues = repository.validate_all()
    assert any("activation evidence digest has changed" in issue.message for issue in issues)

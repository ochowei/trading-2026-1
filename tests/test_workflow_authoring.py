import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import build_parser, main
from trading.core.workflow_authoring import (
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)

FIXED_TIME = datetime(2026, 8, 11, 4, 5, 6, tzinfo=UTC)


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _root_body() -> str:
    return """# Research Workflows

<!-- GENERATED:WORKFLOW_INDEX_START -->
_No workflow versions registered._
<!-- GENERATED:WORKFLOW_INDEX_END -->
"""


def _version_body(title: str) -> str:
    return f"""# {title}

## Work index

<!-- GENERATED:WORK_INDEX_START -->
### Studies

_No studies._

### Changes

_No changes._
<!-- GENERATED:WORK_INDEX_END -->
"""


def _workflow_definition(title: str) -> str:
    return f"""# {title}

## Purpose and decision

Determine whether the documented research decision may proceed under fixed evidence rules.

## Scope and non-goals

This fixture is a complete structural contract and does not submit orders.
"""


def _initialize_root(tmp_path: Path) -> tuple[Path, WorkflowRepository]:
    root = tmp_path / "workflows"
    _write_document(root / "README.md", {"schema_version": 1, "workflows": {}}, _root_body())
    return root, WorkflowRepository(root, now=lambda: FIXED_TIME)


def _register_version(
    root: Path,
    *,
    slug: str = "example-workflow",
    title: str = "Example Workflow",
    version: str = "v001",
    status: str = "draft",
    supersedes: str | None = None,
    source_changes: list[str] | None = None,
    dependencies: list[dict[str, str]] | None = None,
) -> Path:
    registry_path = root / "README.md"
    registry_document = read_markdown_document(registry_path)
    registry = copy.deepcopy(registry_document.metadata)
    workflows = registry["workflows"]
    family = workflows.setdefault(slug, {"title": title, "versions": {}})
    path_name = f"{slug}--{version}"
    family["versions"][version] = {"path": path_name, "status": status}
    _write_document(registry_path, registry, registry_document.body)

    path = root / path_name
    _write_document(
        path / "README.md",
        {
            "workflow": slug,
            "title": title,
            "version": version,
            "definition": "WORKFLOW.md",
            "supersedes": supersedes,
            "derived_from": None,
            "source_changes": source_changes or [],
            "dependencies": dependencies or [],
        },
        _version_body(title),
    )
    (path / "WORKFLOW.md").write_text(_workflow_definition(title), encoding="utf-8")
    return path


def _create_change(version_path: Path, *, number: int = 1) -> Path:
    change_path = version_path / "work" / "changes" / f"tighten-threshold--c{number:03d}"
    _write_document(
        change_path / "README.md",
        {
            "id": f"C{number:03d}",
            "title": "Tighten threshold",
            "workflow": "example-workflow",
            "source_version": "v001",
            "status": "draft",
            "created_at": "2026-08-11",
            "status_changed_at": None,
            "decided_at": None,
            "decided_by": None,
            "released_in": None,
        },
        "# Tighten threshold\n",
    )
    artifacts = {
        "PROPOSAL.md": "# Proposal\n\nTighten the frozen threshold to prevent weak evidence from advancing.\n",
        "IMPACT.md": "# Impact\n\nExisting open studies must pause for an explicit version impact decision.\n",
        "VALIDATION.md": "# Validation\n\nChallenge the combined rule against boundary and incomplete-evidence cases.\n",
        "DECISION.md": "# Decision\n\nAccept after human review because the stricter rule closes an evidence gap.\n",
    }
    for filename, content in artifacts.items():
        (change_path / filename).write_text(content, encoding="utf-8")
    return change_path


def test_empty_registry_is_valid_and_cli_reports_success(tmp_path, capsys) -> None:
    root, repository = _initialize_root(tmp_path)

    assert repository.validate_all() == ()

    main(["workflow", "--root", str(root), "validate", "--all"])
    assert "workflow validation passed" in capsys.readouterr().out


def test_sync_rebuilds_stale_root_and_version_indexes(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    _register_version(root)

    issues = repository.validate_all()
    assert any("generated workflow index is stale" in issue.message for issue in issues)

    repository.sync()

    assert repository.validate_all() == ()
    root_text = (root / "README.md").read_text(encoding="utf-8")
    assert "example-workflow--v001" in root_text


def test_change_transitions_require_completed_artifacts_and_human_approval(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    v1 = _register_version(root)
    repository.sync()
    repository.release(v1, approved_by="research-owner")
    change = _create_change(v1)
    repository.sync()

    repository.transition_change(change, "proposed")
    with pytest.raises(WorkflowAuthoringError, match="requires --approved-by"):
        repository.transition_change(change, "accepted")

    proposal = change / "PROPOSAL.md"
    original_proposal = proposal.read_text(encoding="utf-8")
    proposal.write_text("# Proposal\n\nREPLACE_ME\n", encoding="utf-8")
    with pytest.raises(WorkflowAuthoringError, match="proposed change needs completed PROPOSAL"):
        repository.transition_change(change, "accepted", approved_by="research-owner")
    proposal.write_text(original_proposal, encoding="utf-8")

    repository.transition_change(change, "accepted", approved_by="research-owner")

    metadata = read_markdown_document(change / "README.md").metadata
    assert metadata["status"] == "accepted"
    assert metadata["decided_by"] == "research-owner"
    assert repository.validate_all() == ()


def test_release_supersedes_active_version_and_releases_source_changes(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    v1 = _register_version(root)
    repository.sync()
    repository.release(v1, approved_by="research-owner")
    change = _create_change(v1)
    repository.sync()
    repository.transition_change(change, "proposed")
    repository.transition_change(change, "accepted", approved_by="research-owner")

    dependency = tmp_path / "docs" / "qualification.md"
    dependency.parent.mkdir()
    dependency.write_text("# Qualification\n\nNormative evidence gates.\n", encoding="utf-8")
    change_reference = str(change.relative_to(tmp_path))
    v2 = _register_version(
        root,
        version="v002",
        supersedes="v001",
        source_changes=[change_reference],
        dependencies=[{"path": "docs/qualification.md", "role": "normative"}],
    )
    repository.sync()

    release = repository.release(v2, approved_by="research-owner")

    registry = read_markdown_document(root / "README.md").metadata
    versions = registry["workflows"]["example-workflow"]["versions"]
    assert versions["v001"]["status"] == "superseded"
    assert versions["v002"]["status"] == "active"
    assert read_markdown_document(change / "README.md").metadata["status"] == "released"
    assert release["approved_at"] == "2026-08-11T04:05:06.000000Z"
    assert release["prepared_at"] == release["approved_at"]
    assert "released_at" not in release
    assert release["dependencies"][0]["sha256"]
    assert json.loads((v2 / "RELEASE.json").read_text()) == release
    assert repository.validate_all() == ()

    definition = v2 / "WORKFLOW.md"
    original_definition = definition.read_text(encoding="utf-8")
    definition.write_text(f"{original_definition}\nChanged after release.\n", encoding="utf-8")
    assert any(
        "published WORKFLOW.md digest has changed" in issue.message
        for issue in repository.validate_all()
    )
    definition.write_text(original_definition, encoding="utf-8")

    dependency.write_text("# Qualification\n\nChanged normative rules.\n", encoding="utf-8")
    assert any(
        "active normative dependency digest has changed" in issue.message
        for issue in repository.validate_all()
    )


def test_replacement_release_can_pin_an_intentionally_updated_normative_dependency(
    tmp_path,
) -> None:
    root, repository = _initialize_root(tmp_path)
    dependency = tmp_path / "docs" / "qualification.md"
    dependency.parent.mkdir()
    dependency.write_text("# Qualification\n\nOriginal normative gates.\n", encoding="utf-8")
    dependencies = [{"path": "docs/qualification.md", "role": "normative"}]
    v1 = _register_version(root, dependencies=dependencies)
    repository.sync()
    old_release = repository.release(v1, approved_by="research-owner")
    change = _create_change(v1)
    repository.sync()
    repository.transition_change(change, "proposed")
    repository.transition_change(change, "accepted", approved_by="research-owner")
    v2 = _register_version(
        root,
        version="v002",
        supersedes="v001",
        source_changes=[str(change.relative_to(tmp_path))],
        dependencies=dependencies,
    )
    repository.sync()

    dependency.write_text("# Qualification\n\nApproved replacement gates.\n", encoding="utf-8")
    assert any(
        "active normative dependency digest has changed" in issue.message
        for issue in repository.validate_all()
    )

    new_release = repository.release(v2, approved_by="research-owner")

    assert new_release["dependencies"][0]["sha256"] != old_release["dependencies"][0]["sha256"]
    assert repository.validate_all() == ()


def test_release_refuses_unresolved_changes_without_partial_mutation(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    v1 = _register_version(root)
    repository.sync()
    repository.release(v1, approved_by="research-owner")
    included = _create_change(v1, number=1)
    omitted = _create_change(v1, number=2)
    repository.sync()
    for change in (included, omitted):
        repository.transition_change(change, "proposed")
        repository.transition_change(change, "accepted", approved_by="research-owner")
    v2 = _register_version(
        root,
        version="v002",
        supersedes="v001",
        source_changes=[str(included.relative_to(tmp_path))],
    )
    repository.sync()

    with pytest.raises(WorkflowAuthoringError, match="accepted change must be included"):
        repository.release(v2, approved_by="research-owner")

    registry = read_markdown_document(root / "README.md").metadata
    versions = registry["workflows"]["example-workflow"]["versions"]
    assert versions["v001"]["status"] == "active"
    assert versions["v002"]["status"] == "draft"
    assert not (v2 / "RELEASE.json").exists()
    assert read_markdown_document(included / "README.md").metadata["status"] == "accepted"
    assert read_markdown_document(omitted / "README.md").metadata["status"] == "accepted"


def test_version_abandon_and_retire_are_guarded_transitions(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    draft = _register_version(root)
    repository.sync()

    repository.transition_version(draft, "abandoned")
    registry = read_markdown_document(root / "README.md").metadata
    assert registry["workflows"]["example-workflow"]["versions"]["v001"]["status"] == ("abandoned")

    root2, repository2 = _initialize_root(tmp_path / "second")
    active = _register_version(root2)
    repository2.sync()
    repository2.release(active, approved_by="research-owner")
    open_change = _create_change(active)
    repository2.sync()
    with pytest.raises(WorkflowAuthoringError, match="requires --approved-by"):
        repository2.transition_version(active, "retired")
    with pytest.raises(WorkflowAuthoringError, match="resolve draft change"):
        repository2.transition_version(active, "retired", approved_by="research-owner")
    repository2.transition_change(open_change, "withdrawn")
    repository2.transition_version(active, "retired", approved_by="research-owner")
    assert repository2.validate_all() == ()


def test_cli_has_no_backdated_release_clock(tmp_path) -> None:
    root, _repository = _initialize_root(tmp_path)
    version = _register_version(root)

    args = build_parser().parse_args(
        [
            "workflow",
            "--root",
            str(root),
            "release",
            str(version),
            "--approved-by",
            "research-owner",
        ]
    )
    assert args.workflow_command == "release"
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "workflow",
                "--root",
                str(root),
                "release",
                str(version),
                "--approved-by",
                "research-owner",
                "--prepared-at",
                "2020-01-01T00:00:00Z",
            ]
        )

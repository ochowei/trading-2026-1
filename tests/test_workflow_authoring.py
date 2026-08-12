import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import build_parser, main
from trading.core.policy_authoring import PolicyRepository
from trading.core.workflow_authoring import (
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)
from trading.core.workflow_studies import WorkflowStudyService

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
    policies: list[dict[str, str]] | None = None,
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
            **({"policies": policies} if policies is not None else {}),
        },
        _version_body(title),
    )
    (path / "WORKFLOW.md").write_text(_workflow_definition(title), encoding="utf-8")
    return path


def _released_policy(tmp_path: Path, *, family: str = "market-policy") -> dict[str, str]:
    root = tmp_path / "policies"
    path_name = f"{family}--v001"
    _write_document(
        root / "README.md",
        {
            "schema_version": 1,
            "policies": {
                family: {
                    "title": "Market Policy",
                    "versions": {"v001": {"path": path_name, "status": "draft"}},
                }
            },
        },
        """# Policies

<!-- GENERATED:POLICY_INDEX_START -->
stale
<!-- GENERATED:POLICY_INDEX_END -->
""",
    )
    version = root / path_name
    implementation = tmp_path / "src" / "trading" / "policy_fixture.py"
    implementation.parent.mkdir(parents=True, exist_ok=True)
    implementation.write_text("POLICY = 1\n", encoding="utf-8")
    conformance = tmp_path / "tests" / "test_policy_fixture.py"
    conformance.parent.mkdir(exist_ok=True)
    conformance.write_text("def test_policy():\n    assert True\n", encoding="utf-8")
    _write_document(
        version / "README.md",
        {
            "policy": family,
            "title": "Market Policy",
            "version": "v001",
            "definition": "POLICY.md",
            "config": "policy.yaml",
            "supersedes": None,
            "implementation": ["src/trading/policy_fixture.py"],
            "conformance": ["tests/test_policy_fixture.py"],
        },
        "# Market Policy\n",
    )
    (version / "POLICY.md").write_text(
        "# Market Policy\n\nA complete executable market policy for workflow tests.\n",
        encoding="utf-8",
    )
    (version / "policy.yaml").write_text(
        f"schema_version: 1\nfamily: {family}\nversion: v001\nkind: test\nvalues:\n  calendar: XNYS\n",
        encoding="utf-8",
    )
    repository = PolicyRepository(
        root,
        now=lambda: FIXED_TIME,
        conformance_runner=lambda _paths: None,
    )
    repository.sync()
    repository.release(version, approved_by="policy-owner")
    release_digest = hashlib.sha256((version / "RELEASE.json").read_bytes()).hexdigest()
    return {
        "family": family,
        "version": "v001",
        "path": f"policies/{path_name}",
        "release_digest": release_digest,
    }


def test_repository_with_policy_registry_requires_exact_released_policy_pins(tmp_path) -> None:
    policy = _released_policy(tmp_path)
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root, policies=[policy])
    repository.sync()

    release = repository.release(version, approved_by="research-owner")

    assert release["policies"] == [policy]
    assert repository.validate_all() == ()

    release_path = tmp_path / policy["path"] / "RELEASE.json"
    release_path.write_text("{}\n", encoding="utf-8")
    assert any(
        "policy release digest has changed" in issue.message for issue in repository.validate_all()
    )


def test_repository_with_policy_registry_rejects_unpinned_workflow_release(tmp_path) -> None:
    _released_policy(tmp_path)
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root)
    repository.sync()

    with pytest.raises(WorkflowAuthoringError, match="explicit policy pins"):
        repository.release(version, approved_by="research-owner")


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


def _complete_study_plan(study_path: Path) -> None:
    (study_path / "HYPOTHESIS.md").write_text(
        "# Hypothesis\n\nThe frozen candidate must exceed its benchmark under every declared gate.\n",
        encoding="utf-8",
    )
    (study_path / "PLAN.md").write_text(
        "# Plan\n\nUse the pinned snapshot and workflow stages; fail on any missing gate or identity.\n",
        encoding="utf-8",
    )


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

    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    open_study = studies.initialize(
        v1,
        study_slug="open-version-boundary",
        title="Open version boundary",
        created_by="research-agent",
    )
    _complete_study_plan(open_study)
    studies.preregister(open_study, approved_by="research-owner")
    studies.transition(open_study, "running", actor="research-agent")
    with pytest.raises(WorkflowAuthoringError, match="resolve running study"):
        repository.release(v2, approved_by="research-owner")
    studies.transition(
        open_study,
        "paused",
        actor="research-agent",
        reason="Replacement workflow impact must be resolved first",
    )

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


def test_study_lifecycle_freezes_plan_evidence_and_conclusion(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root)
    repository.sync()
    repository.release(version, approved_by="research-owner")
    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)

    study = studies.initialize(
        version,
        study_slug="forward-gate",
        title="Forward gate study",
        created_by="research-agent",
    )
    second = studies.initialize(
        version,
        study_slug="second-gate",
        title="Second gate study",
        created_by="research-agent",
        revisits=str(study.relative_to(tmp_path)),
    )

    assert study.name == "forward-gate--s001"
    assert second.name == "second-gate--s002"
    assert read_markdown_document(second / "README.md").metadata["revisits"] == str(
        study.relative_to(tmp_path)
    )
    assert read_markdown_document(study / "README.md").metadata["status"] == "draft"
    _complete_study_plan(study)
    registration = studies.preregister(study, approved_by="research-owner")
    assert registration["approved_at"] == "2026-08-11T04:05:06.000000Z"
    assert registration["workflow_sha256"]

    original_plan = (study / "PLAN.md").read_text(encoding="utf-8")
    (study / "PLAN.md").write_text(
        f"{original_plan}\nPost-registration change.\n", encoding="utf-8"
    )
    assert any(
        "preregistered content digest has changed" in issue.message
        for issue in repository.validate_all()
    )
    (study / "PLAN.md").write_text(original_plan, encoding="utf-8")

    studies.transition(study, "running", actor="research-agent")
    with pytest.raises(WorkflowAuthoringError, match="EVIDENCE.md must be complete"):
        studies.transition(study, "awaiting-review", actor="research-agent")
    (study / "EVIDENCE.md").write_text(
        "# Evidence\n\nAll declared gates ran against immutable result manifests and exact snapshots.\n",
        encoding="utf-8",
    )
    studies.transition(study, "awaiting-review", actor="research-agent")
    (study / "CONCLUSION.md").write_text(
        "# Conclusion\n\nPass: every frozen gate succeeded and each claim traces to immutable evidence.\n",
        encoding="utf-8",
    )
    completion = studies.complete(study, outcome="pass", reviewed_by="independent-reviewer")

    assert completion["outcome"] == "pass"
    assert completion["evidence_sha256"]
    assert read_markdown_document(study / "README.md").metadata["status"] == "completed"
    assert repository.validate_all() == ()

    (study / "EVIDENCE.md").write_text(
        "# Evidence\n\nEvidence was modified after completion, which must invalidate the record.\n",
        encoding="utf-8",
    )
    assert any(
        "completed study artifact has changed" in issue.message
        for issue in repository.validate_all()
    )


def test_study_transitions_are_guarded_and_require_reasons(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root)
    repository.sync()
    repository.release(version, approved_by="research-owner")
    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    study = studies.initialize(
        version,
        study_slug="pause-boundary",
        title="Pause boundary",
        created_by="research-agent",
    )
    _complete_study_plan(study)
    studies.preregister(study, approved_by="research-owner")

    with pytest.raises(WorkflowAuthoringError, match="only an awaiting-review study"):
        studies.complete(study, outcome="pass", reviewed_by="reviewer")
    studies.transition(study, "running", actor="research-agent")
    with pytest.raises(WorkflowAuthoringError, match="paused transition requires --reason"):
        studies.transition(study, "paused", actor="research-agent")
    studies.transition(
        study,
        "paused",
        actor="research-agent",
        reason="Required market-data snapshot is unavailable",
    )
    studies.transition(study, "running", actor="research-agent")

    draft = studies.initialize(
        version,
        study_slug="cancelled-draft",
        title="Cancelled draft",
        created_by="research-agent",
    )
    with pytest.raises(WorkflowAuthoringError, match="cancelled transition requires --reason"):
        studies.transition(draft, "cancelled", actor="research-agent")
    studies.transition(
        draft,
        "cancelled",
        actor="research-agent",
        reason="The proposed question duplicates an existing study",
    )
    assert repository.validate_all() == ()


def test_study_creation_and_preregistration_require_active_workflow(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root)
    repository.sync()
    repository.release(version, approved_by="research-owner")
    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    draft = studies.initialize(
        version,
        study_slug="retirement-boundary",
        title="Retirement boundary",
        created_by="research-agent",
    )
    _complete_study_plan(draft)
    with pytest.raises(WorkflowAuthoringError, match="resolve draft study"):
        repository.transition_version(version, "retired", approved_by="research-owner")
    studies.transition(
        draft,
        "cancelled",
        actor="research-agent",
        reason="Workflow retirement ended this draft",
    )
    repository.transition_version(version, "retired", approved_by="research-owner")

    with pytest.raises(WorkflowAuthoringError, match="active workflow version"):
        studies.initialize(
            version,
            study_slug="too-late",
            title="Too late",
            created_by="research-agent",
        )


def test_cli_exposes_study_lifecycle_without_backdating_options(tmp_path, capsys) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_version(root)
    repository.sync()
    repository.release(version, approved_by="research-owner")

    main(
        [
            "workflow",
            "--root",
            str(root),
            "study",
            "init",
            str(version),
            "--slug",
            "cli-study",
            "--title",
            "CLI study",
            "--created-by",
            "research-agent",
        ]
    )
    assert "workflow study initialized" in capsys.readouterr().out
    study = version / "work" / "studies" / "cli-study--s001"
    _complete_study_plan(study)
    main(
        [
            "workflow",
            "--root",
            str(root),
            "study",
            "preregister",
            str(study),
            "--approved-by",
            "research-owner",
        ]
    )
    main(
        [
            "workflow",
            "--root",
            str(root),
            "study",
            "transition",
            str(study),
            "--to",
            "running",
            "--by",
            "research-agent",
        ]
    )
    (study / "EVIDENCE.md").write_text(
        "# Evidence\n\nEvery planned CLI stage produced an exact immutable evidence identity.\n",
        encoding="utf-8",
    )
    main(
        [
            "workflow",
            "--root",
            str(root),
            "study",
            "transition",
            str(study),
            "--to",
            "awaiting-review",
            "--by",
            "research-agent",
        ]
    )
    (study / "CONCLUSION.md").write_text(
        "# Conclusion\n\nPass: the exact CLI evidence satisfies every frozen outcome rule.\n",
        encoding="utf-8",
    )
    main(
        [
            "workflow",
            "--root",
            str(root),
            "study",
            "complete",
            str(study),
            "--outcome",
            "pass",
            "--reviewed-by",
            "independent-reviewer",
        ]
    )
    assert "workflow study completed" in capsys.readouterr().out
    assert repository.validate_all() == ()

    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "workflow",
                "--root",
                str(root),
                "study",
                "preregister",
                str(version / "work" / "studies" / "cli-study--s001"),
                "--approved-by",
                "research-owner",
                "--approved-at",
                "2020-01-01T00:00:00Z",
            ]
        )

import copy
import hashlib
import json
import shutil
import subprocess
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import build_parser, main
from trading.core.policy_authoring import PolicyRepository
from trading.core.study_qualification import REQUIRED_STUDY_TIME_CHALLENGES
from trading.core.workflow_authoring import (
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
    render_markdown_document,
)
from trading.core.workflow_studies import WorkflowStudyService
from trading.research_data import ResearchDefinitionStore, formal_trial_id
from trading.research_definitions import ResearchDefinitionRegistry, resolve_workflow_policy_set

FIXED_TIME = datetime(2026, 8, 11, 4, 5, 6, tzinfo=UTC)


def test_tracked_workflow_history_validates_without_format_migration() -> None:
    repository = WorkflowRepository(Path("workflows"))

    assert repository.validate_all() == ()

    change_directories = sorted(Path("workflows").glob("*/work/changes/*--c[0-9][0-9][0-9]"))
    assert change_directories
    for change_directory in change_directories:
        assert {
            "README.md",
            "PROPOSAL.md",
            "IMPACT.md",
            "VALIDATION.md",
            "DECISION.md",
        }.issubset(path.name for path in change_directory.iterdir())
        assert not (change_directory / "CHANGE.md").exists()


def test_authoring_skill_routes_modes_to_progressive_disclosure_references() -> None:
    skill_root = Path(".agents/skills/trading-author-workflow")
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    required_references = {
        "core.md",
        "create.md",
        "evolve.md",
        "remove.md",
        "release.md",
        "impact.md",
    }

    assert required_references == {
        path.name
        for path in (skill_root / "references").glob("*.md")
        if path.name != "workflow-authoring-contract.md"
    }
    assert "Read `references/core.md`" in skill_text
    assert "Read `references/create.md`" in skill_text
    assert "Read `references/evolve.md`" in skill_text
    assert "Read `references/remove.md`" in skill_text
    assert "Read `references/release.md`" in skill_text
    assert "Read `references/impact.md`" in skill_text
    assert "Read\n[`references/workflow-authoring-contract.md`]" not in skill_text

    compatibility_pointer = (
        skill_root / "references" / "workflow-authoring-contract.md"
    ).read_text(encoding="utf-8")
    assert len(compatibility_pointer.splitlines()) <= 30
    for reference in sorted(required_references):
        assert reference in compatibility_pointer


def test_study_skills_use_shared_study_governance_reference() -> None:
    shared_reference = Path(".agents/rules/workflow-study-governance.md")
    assert shared_reference.is_file()

    for skill_path in (
        Path(".agents/skills/trading-operate-workflow/SKILL.md"),
        Path(".agents/skills/trading-evaluate-study/SKILL.md"),
    ):
        text = skill_path.read_text(encoding="utf-8")
        assert ".agents/rules/workflow-study-governance.md" in text
        assert "workflow-authoring-contract.md" not in text


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


def test_candidate_freeze_evidence_requires_canonical_content_addressed_bytes(tmp_path) -> None:
    root, _repository = _initialize_root(tmp_path)
    indexed: set[Path] = set()
    repository = WorkflowRepository(
        root,
        now=lambda: FIXED_TIME,
        git_index_checker=lambda path: path.resolve() in indexed,
    )
    freeze = (
        root
        / "example-workflow--v001"
        / "work"
        / "studies"
        / "example--s001"
        / "CANDIDATE_FREEZE.json"
    )
    content = b"# Exact evidence\n"
    digest = hashlib.sha256(content).hexdigest()
    freeze.parent.mkdir(parents=True)
    freeze.write_text(
        json.dumps({"schema_version": 1, "development_evidence_sha256": digest}) + "\n",
        encoding="utf-8",
    )

    issues = []
    repository._validate_candidate_freeze_evidence(issues)
    assert len(issues) == 1
    assert "missing research evidence" in issues[0].message

    artifact = tmp_path / "results" / "research-evidence" / f"{digest}.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(content)
    issues = []
    repository._validate_candidate_freeze_evidence(issues)
    assert len(issues) == 1
    assert "not in the Git index" in issues[0].message

    indexed.add(artifact.resolve())
    issues = []
    repository._validate_candidate_freeze_evidence(issues)
    assert issues == []

    artifact.write_bytes(b"drifted\n")
    issues = []
    repository._validate_candidate_freeze_evidence(issues)
    assert len(issues) == 1
    assert "checksum has changed" in issues[0].message


def test_candidate_freeze_evidence_survives_git_gc_and_fresh_clone(tmp_path) -> None:
    source = tmp_path / "source"
    root, _repository = _initialize_root(source)
    content = b"# Fresh-clone evidence\n"
    digest = hashlib.sha256(content).hexdigest()
    freeze = root / "example--v001" / "work" / "studies" / "example--s001" / "CANDIDATE_FREEZE.json"
    freeze.parent.mkdir(parents=True)
    freeze.write_text(
        json.dumps({"schema_version": 1, "development_evidence_sha256": digest}) + "\n",
        encoding="utf-8",
    )
    artifact = source / "results" / "research-evidence" / f"{digest}.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(content)
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=source, check=True)
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=source, check=True)
    subprocess.run(["git", "gc", "--prune=now"], cwd=source, check=True)

    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(source), str(clone)], check=True)
    issues: list = []
    WorkflowRepository(clone / "workflows")._validate_candidate_freeze_evidence(issues)
    assert issues == []


def test_git_index_check_rejects_worktree_bytes_that_differ_from_staged_blob(tmp_path) -> None:
    root, _repository = _initialize_root(tmp_path)
    freeze = root / "example--v001" / "work" / "studies" / "example--s001" / "CANDIDATE_FREEZE.json"
    current = b"worktree bytes\n"
    digest = hashlib.sha256(current).hexdigest()
    artifact = tmp_path / "results" / "research-evidence" / f"{digest}.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"staged bytes\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", str(artifact.relative_to(tmp_path))], cwd=tmp_path, check=True)
    artifact.write_bytes(current)
    freeze.parent.mkdir(parents=True)
    freeze.write_text(
        json.dumps({"schema_version": 1, "development_evidence_sha256": digest}) + "\n",
        encoding="utf-8",
    )
    # Canonical path for the worktree bytes exists in the index, but its staged bytes differ.
    issues = []
    WorkflowRepository(root)._validate_candidate_freeze_evidence(issues)
    assert len(issues) == 1
    assert "not in the Git index" in issues[0].message


@pytest.mark.parametrize(
    "relative",
    [
        "results/qualification-evidence/" + "a" * 64 + ".json",
        "results/study-evidence/example--s001/challenges/cash.json",
    ],
)
def test_repository_gitignore_tracks_terminal_evidence_namespaces(
    tmp_path,
    relative: str,
) -> None:
    (tmp_path / ".gitignore").write_text(
        Path(".gitignore").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    artifact = tmp_path / relative
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", relative],
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 1


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
    capabilities: list[str] | None = None,
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
            **({"capabilities": capabilities} if capabilities is not None else {}),
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


def test_pinned_reference_companion_digest_is_released_and_drift_checked(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    companion = tmp_path / "docs" / "stages.md"
    companion.parent.mkdir()
    companion.write_text("# Stages\n\nExplanatory only.\n", encoding="utf-8")
    version = _register_version(
        root,
        dependencies=[{"path": "docs/stages.md", "role": "reference", "pinned": True}],
    )
    repository.sync()

    release = repository.release(version, approved_by="research-owner")

    assert release["dependencies"] == [
        {
            "path": "docs/stages.md",
            "role": "reference",
            "pinned": True,
            "sha256": hashlib.sha256(companion.read_bytes()).hexdigest(),
        }
    ]
    companion.write_text("# Stages\n\nChanged after release.\n", encoding="utf-8")
    assert any(
        "active pinned dependency digest has changed" in issue.message
        for issue in repository.validate_all()
    )


def test_retired_release_still_rejects_pinned_reference_drift(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    companion = tmp_path / "docs" / "stages.md"
    companion.parent.mkdir()
    companion.write_text("# Stages\n\nPinned bytes.\n", encoding="utf-8")
    version = _register_version(
        root,
        dependencies=[{"path": "docs/stages.md", "role": "reference", "pinned": True}],
    )
    repository.sync()
    repository.release(version, approved_by="research-owner")
    repository.transition_version(version, "retired", approved_by="research-owner")

    companion.write_text("# Stages\n\nDrifted after retirement.\n", encoding="utf-8")

    assert any(
        "released pinned dependency digest has changed" in issue.message
        for issue in repository.validate_all()
    )


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


def test_cli_create_previews_then_creates_initial_workflow(tmp_path, capsys) -> None:
    shutil.copytree("policies", tmp_path / "policies")
    shutil.copytree("src", tmp_path / "src")
    shutil.copytree("tests/policies", tmp_path / "tests" / "policies")
    root, _repository = _initialize_root(tmp_path)
    definition = tmp_path / "docs" / "example-workflow.md"
    definition.parent.mkdir()
    definition.write_text(_workflow_definition("Example Workflow"), encoding="utf-8")
    current_v008 = read_markdown_document(
        Path("workflows/strategy-forward-replication-research--v008/README.md")
    ).metadata
    request = tmp_path / "create-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "example-workflow",
                "title": "Example Workflow",
                "definition_path": "docs/example-workflow.md",
                "authoring_basis": "Confirmed test request with a complete workflow definition.",
                "policies": current_v008["policies"],
                "dependencies": [],
                "capabilities": [],
                "derived_from": None,
            }
        ),
        encoding="utf-8",
    )
    registry_before = (root / "README.md").read_bytes()

    main(
        [
            "workflow",
            "--root",
            str(root),
            "create",
            "--request",
            str(request),
            "--dry-run",
        ]
    )

    preview = json.loads(capsys.readouterr().out)
    assert preview == {
        "schema_version": 1,
        "operation": "create",
        "workflow": "example-workflow",
        "version": "v001",
        "target": "workflows/example-workflow--v001",
        "source_version": None,
        "source_changes": [],
        "policies": current_v008["policies"],
        "dependencies": [],
        "authoring_basis": "Confirmed test request with a complete workflow definition.",
        "changes": [
            {"action": "create", "path": "workflows/example-workflow--v001/README.md"},
            {"action": "create", "path": "workflows/example-workflow--v001/WORKFLOW.md"},
            {"action": "update", "path": "workflows/README.md"},
        ],
        "warnings": [],
        "blocking_issues": [],
        "remaining_decisions": [],
    }
    assert not (root / "example-workflow--v001").exists()
    assert (root / "README.md").read_bytes() == registry_before

    main(
        [
            "workflow",
            "--root",
            str(root),
            "create",
            "--request",
            str(request),
        ]
    )

    assert "workflow created: example-workflow@v001" in capsys.readouterr().out
    version = root / "example-workflow--v001"
    metadata = read_markdown_document(version / "README.md").metadata
    assert metadata["workflow"] == "example-workflow"
    assert metadata["version"] == "v001"
    assert metadata["source_changes"] == []
    assert metadata["policies"] == current_v008["policies"]
    assert (version / "WORKFLOW.md").read_bytes() == definition.read_bytes()
    assert WorkflowRepository(root).validate_all() == ()
    with pytest.raises(SystemExit, match="workflow family already exists"):
        main(
            [
                "workflow",
                "--root",
                str(root),
                "create",
                "--request",
                str(request),
                "--dry-run",
            ]
        )


def test_create_request_rejects_authority_fields_and_invalid_pins(tmp_path) -> None:
    shutil.copytree("policies", tmp_path / "policies")
    shutil.copytree("src", tmp_path / "src")
    shutil.copytree("tests/policies", tmp_path / "tests" / "policies")
    root, _repository = _initialize_root(tmp_path)
    definition = tmp_path / "docs" / "example-workflow.md"
    definition.parent.mkdir()
    definition.write_text(_workflow_definition("Example Workflow"), encoding="utf-8")
    policies = read_markdown_document(
        Path("workflows/strategy-forward-replication-research--v008/README.md")
    ).metadata["policies"]
    request = tmp_path / "create-request.json"
    base = {
        "schema_version": 1,
        "slug": "example-workflow",
        "title": "Example Workflow",
        "definition_path": "docs/example-workflow.md",
        "authoring_basis": "Confirmed request with a complete workflow definition.",
        "policies": policies,
        "dependencies": [],
        "capabilities": [],
        "derived_from": None,
    }

    request.write_text(json.dumps({**base, "status": "active"}), encoding="utf-8")
    with pytest.raises(SystemExit, match="unknown authoring request fields: status"):
        main(["workflow", "--root", str(root), "create", "--request", str(request), "--dry-run"])

    request.write_text(json.dumps({**base, "policies": policies[:-1]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="requires four policy kinds"):
        main(["workflow", "--root", str(root), "create", "--request", str(request), "--dry-run"])

    request.write_text(
        json.dumps(
            {
                **base,
                "dependencies": [{"path": "docs/missing.md", "role": "normative"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="dependency file does not exist"):
        main(["workflow", "--root", str(root), "create", "--request", str(request), "--dry-run"])


def test_cli_change_create_allocates_next_identity_and_preserves_draft(tmp_path, capsys) -> None:
    root, repository = _initialize_root(tmp_path)
    active = _register_version(root)
    repository.sync()
    repository.release(active, approved_by="research-owner")
    _create_change(active, number=2)
    repository.sync()
    active_readme_before = (active / "README.md").read_bytes()
    proposal = tmp_path / "docs" / "proposal.md"
    impact = tmp_path / "docs" / "impact.md"
    proposal.parent.mkdir()
    proposal.write_text(
        "# Proposal\n\nTighten the frozen threshold to prevent weak evidence from advancing.\n",
        encoding="utf-8",
    )
    impact.write_text(
        "# Impact\n\nPause open studies until a human records the version-boundary decision.\n",
        encoding="utf-8",
    )
    request = tmp_path / "change-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workflow": "example-workflow",
                "slug": "tighten-threshold",
                "title": "Tighten threshold",
                "proposal_path": "docs/proposal.md",
                "impact_path": "docs/impact.md",
                "validation_path": None,
                "decision_path": None,
                "propose": False,
            }
        ),
        encoding="utf-8",
    )

    main(
        [
            "workflow",
            "--root",
            str(root),
            "change",
            "create",
            "--request",
            str(request),
            "--dry-run",
        ]
    )

    preview = json.loads(capsys.readouterr().out)
    target = "workflows/example-workflow--v001/work/changes/tighten-threshold--c003"
    assert preview["operation"] == "change-create"
    assert preview["workflow"] == "example-workflow"
    assert preview["version"] == "v001"
    assert preview["target"] == target
    assert preview["changes"] == [
        {"action": "create", "path": f"{target}/{filename}"}
        for filename in ("README.md", "PROPOSAL.md", "IMPACT.md", "VALIDATION.md", "DECISION.md")
    ] + [{"action": "update", "path": "workflows/example-workflow--v001/README.md"}]
    assert not (active / "work" / "changes" / "tighten-threshold--c003").exists()
    assert (active / "README.md").read_bytes() == active_readme_before

    main(
        [
            "workflow",
            "--root",
            str(root),
            "change",
            "create",
            "--request",
            str(request),
        ]
    )

    assert "workflow change created: C003" in capsys.readouterr().out
    change = active / "work" / "changes" / "tighten-threshold--c003"
    metadata = read_markdown_document(change / "README.md").metadata
    assert metadata["status"] == "draft"
    assert metadata["created_at"] == datetime.now(UTC).date().isoformat()
    assert (change / "PROPOSAL.md").read_bytes() == proposal.read_bytes()
    assert (change / "IMPACT.md").read_bytes() == impact.read_bytes()
    assert WorkflowRepository(root).validate_all() == ()

    payload = json.loads(request.read_text(encoding="utf-8"))
    payload.update({"slug": "tighten-threshold-again", "propose": True})
    request.write_text(json.dumps(payload), encoding="utf-8")
    main(
        [
            "workflow",
            "--root",
            str(root),
            "change",
            "create",
            "--request",
            str(request),
        ]
    )
    proposed = active / "work" / "changes" / "tighten-threshold-again--c004"
    assert read_markdown_document(proposed / "README.md").metadata["status"] == "proposed"


def test_cli_evolve_aggregates_accepted_changes_and_updates_existing_draft(
    tmp_path, capsys
) -> None:
    shutil.copytree("policies", tmp_path / "policies")
    shutil.copytree("src", tmp_path / "src")
    shutil.copytree("tests/policies", tmp_path / "tests" / "policies")
    policies = read_markdown_document(
        Path("workflows/strategy-forward-replication-research--v008/README.md")
    ).metadata["policies"]
    root, repository = _initialize_root(tmp_path)
    active = _register_version(root, policies=policies)
    repository.sync()
    repository.release(active, approved_by="research-owner")
    changes = [_create_change(active, number=number) for number in (1, 2)]
    repository.sync()
    for change in changes:
        repository.transition_change(change, "proposed")
        repository.transition_change(change, "accepted", approved_by="research-owner")
    definition = tmp_path / "docs" / "replacement.md"
    definition.parent.mkdir()
    definition.write_text(_workflow_definition("Example Workflow v2"), encoding="utf-8")
    request = tmp_path / "evolve-request.json"

    def write_request(authoring_basis: str) -> None:
        request.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "workflow": "example-workflow",
                    "title": "Example Workflow",
                    "definition_path": "docs/replacement.md",
                    "authoring_basis": authoring_basis,
                    "policies": policies,
                    "dependencies": [],
                    "capabilities": [],
                }
            ),
            encoding="utf-8",
        )

    write_request("Accepted C001 and C002 with combined impact review.")
    registry_before = (root / "README.md").read_bytes()
    active_readme_before = (active / "README.md").read_bytes()
    main(
        [
            "workflow",
            "--root",
            str(root),
            "evolve",
            "--request",
            str(request),
            "--dry-run",
        ]
    )
    preview = json.loads(capsys.readouterr().out)
    assert preview["operation"] == "evolve"
    assert preview["version"] == "v002"
    assert preview["target"] == "workflows/example-workflow--v002"
    assert not (root / "example-workflow--v002").exists()
    assert (root / "README.md").read_bytes() == registry_before
    assert (active / "README.md").read_bytes() == active_readme_before

    main(["workflow", "--root", str(root), "evolve", "--request", str(request)])
    assert "workflow draft evolved: example-workflow@v002" in capsys.readouterr().out
    draft = root / "example-workflow--v002"
    metadata = read_markdown_document(draft / "README.md").metadata
    assert metadata["supersedes"] == "v001"
    assert metadata["source_changes"] == [
        "workflows/example-workflow--v001/work/changes/tighten-threshold--c001",
        "workflows/example-workflow--v001/work/changes/tighten-threshold--c002",
    ]

    write_request("Updated wording for accepted C001 and C002 after combined review.")
    main(
        [
            "workflow",
            "--root",
            str(root),
            "evolve",
            "--request",
            str(request),
            "--dry-run",
        ]
    )
    update_preview = json.loads(capsys.readouterr().out)
    assert update_preview["version"] == "v002"
    assert {item["action"] for item in update_preview["changes"]} == {"update"}
    main(["workflow", "--root", str(root), "evolve", "--request", str(request)])
    assert not (root / "example-workflow--v003").exists()
    assert WorkflowRepository(root).validate_all() == ()


def test_evolve_rejects_change_without_human_decision(tmp_path) -> None:
    root, repository = _initialize_root(tmp_path)
    active = _register_version(root)
    repository.sync()
    repository.release(active, approved_by="research-owner")
    change = _create_change(active)
    repository.sync()
    repository.transition_change(change, "proposed")
    definition = tmp_path / "docs" / "replacement.md"
    definition.parent.mkdir()
    definition.write_text(_workflow_definition("Example Workflow v2"), encoding="utf-8")
    request = tmp_path / "evolve-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workflow": "example-workflow",
                "title": "Example Workflow",
                "definition_path": "docs/replacement.md",
                "authoring_basis": "Proposal awaits a human decision.",
                "policies": [],
                "dependencies": [],
                "capabilities": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="human decision"):
        main(["workflow", "--root", str(root), "evolve", "--request", str(request), "--dry-run"])
    assert not (root / "example-workflow--v002").exists()


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
        "active pinned dependency digest has changed" in issue.message
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
        "active pinned dependency digest has changed" in issue.message
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


def test_cli_exposes_guarded_candidate_freeze_without_backdated_clock() -> None:
    args = build_parser().parse_args(
        [
            "workflow",
            "study",
            "freeze-candidate",
            "workflows/example--v001/work/studies/example--s001",
            "--selection",
            "development-selection.json",
            "--approved-by",
            "owner@example.com",
        ]
    )
    assert args.workflow_study_command == "freeze-candidate"
    assert not hasattr(args, "approved_at")


def test_cli_dispatches_guarded_candidate_freeze(tmp_path, capsys, monkeypatch) -> None:
    captured = {}

    def freeze_candidate(_self, study_path, *, selection_path, approved_by):
        captured.update(
            study_path=study_path,
            selection_path=selection_path,
            approved_by=approved_by,
        )
        return {"study_id": "S001"}

    monkeypatch.setattr(WorkflowStudyService, "freeze_candidate", freeze_candidate)
    main(
        [
            "workflow",
            "--root",
            str(tmp_path / "workflows"),
            "study",
            "freeze-candidate",
            "workflows/example--v001/work/studies/example--s001",
            "--selection",
            "development-selection.json",
            "--approved-by",
            "owner@example.com",
        ]
    )

    assert captured == {
        "study_path": Path("workflows/example--v001/work/studies/example--s001"),
        "selection_path": Path("development-selection.json"),
        "approved_by": "owner@example.com",
    }
    assert "workflow candidate frozen: S001" in capsys.readouterr().out


def test_public_cli_dry_run_compiles_real_structured_study_end_to_end(
    tmp_path,
    capsys,
) -> None:
    """Exercise release -> study freeze -> exact compiler without provider access or mocks."""
    current_v008 = read_markdown_document(
        Path("workflows/strategy-forward-replication-research--v008/README.md")
    ).metadata
    (tmp_path / "policies").symlink_to(Path("policies").resolve(), target_is_directory=True)
    shutil.copytree("src", tmp_path / "src")
    shutil.copytree("tests", tmp_path / "tests")
    root, repository = _initialize_root(tmp_path)
    version = _register_version(
        root,
        policies=copy.deepcopy(current_v008["policies"]),
        capabilities=["study-time-retrospective-v1"],
    )
    (version / "WORKFLOW.md").write_text(
        _workflow_definition("Example Workflow")
        + "\n## Retrospective route\n\nstudy-time-retrospective is authorized.\n",
        encoding="utf-8",
    )
    repository.sync()
    repository.release(version, approved_by="owner@example.com")

    service = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    study = service.initialize(
        version,
        study_slug="structured-public-path",
        title="Structured public path",
        created_by="researcher@example.com",
        route="study-time-retrospective",
    )
    _complete_study_plan(study)

    identities = (
        "fxi-atr-band-mean-reversion/atr-band-candidate",
        "fxi-atr-band-mean-reversion/pullback-wr-baseline",
    )
    source_registry = ResearchDefinitionRegistry()
    policy_set = resolve_workflow_policy_set(version)
    definition_store = ResearchDefinitionStore(tmp_path / "definition-store", publish=False)
    frozen_family = []
    for identity in identities:
        strategy = source_registry.load(identity)
        snapshot = strategy.capture_research_definition(definition_store, policy_set)
        declaration = strategy.declare_experiment_trial()
        frozen_family.append(
            {
                "source_identity": identity,
                "trial_id": formal_trial_id(declaration.family, snapshot.fingerprint),
                "definition_fingerprint": snapshot.fingerprint,
            }
        )

    spec_path = study / "QUALIFICATION_SPEC.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec.update(
        evidence_justification="Historical outcomes may have been inspected before this study.",
        prior_selection_history_incomplete=False,
    )
    spec["calendar"] = {
        "warmup_start": "2009-01-01",
        "warmup_end": "2009-12-31",
        "development_years": [2010, 2011, 2012],
        "quarantine_years": [2013],
        "evaluation_years": [2014, 2015, 2016, 2017, 2018],
    }
    spec["family"] = {
        "maximum_trials": len(identities),
        "baseline_identity": identities[1],
        "members": [
            {
                "identity": identity,
                "source_sha256": hashlib.sha256(
                    source_registry.resolve(identity).read_bytes()
                ).hexdigest(),
                "role": "selection-candidate" if index == 0 else "family-baseline",
            }
            for index, identity in enumerate(identities)
        ],
        "shared_sources": [],
    }
    spec["execution"] = {
        "maximum_holding_sessions": 20,
        "execution_lag_sessions": 1,
        "dependency_sessions": 21,
        "embargo_sessions": 1,
        "stress_drawdown_limit": "0.20",
    }
    spec["benchmarks"] = {
        "random_seed": 7,
        "random_samples": 100,
        "bootstrap_repetitions": 100,
        "bootstrap_block_sessions": 20,
    }
    spec["required_challenges"] = [
        {
            "id": challenge,
            "evidence_identity": f"{challenge}-evidence",
            "applies_to": {
                "kind": (
                    "benchmark"
                    if challenge in {"cash", "random-entry"}
                    else "trial"
                    if challenge == "family-baseline"
                    else "method"
                ),
                "identities": [
                    challenge
                    if challenge in {"cash", "random-entry"}
                    else identities[1]
                    if challenge == "family-baseline"
                    else f"{challenge}-method"
                ],
            },
            "gate": {"metric": "passed", "operator": "=", "threshold": True},
        }
        for challenge in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
    ]
    spec_path.write_text(json.dumps(spec, sort_keys=True) + "\n", encoding="utf-8")

    service.preregister(study, approved_by="owner@example.com")
    service.transition(
        study,
        "running",
        actor="researcher@example.com",
        approved_by="owner@example.com",
    )
    selection_path = tmp_path / "development-selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "selected_candidate": frozen_family[0],
                "family_baseline": frozen_family[1],
                "complete_family": frozen_family,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    service.freeze_candidate(
        study,
        selection_path=selection_path,
        approved_by="owner@example.com",
    )

    qualification_registry = tmp_path / "state" / "qualification-registry.json"
    trial_registry = tmp_path / "results" / "trial_registry.json"
    main(
        [
            "qualification",
            "plan",
            "register-study",
            "--study",
            str(study),
            "--path",
            str(qualification_registry),
            "--trial-registry-path",
            str(trial_registry),
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out
    assert "study qualification plan compiled (dry-run)" in output
    assert "frozen family trials: 2" in output
    assert "evidence role: study-time-retrospective" in output
    assert not qualification_registry.exists()
    assert not trial_registry.exists()


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


def test_capability_scoped_study_requires_explicit_route_at_creation(tmp_path, monkeypatch) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_version(
        root,
        capabilities=["study-time-retrospective-v1"],
    )
    repository.sync()
    repository.release(version, approved_by="research-owner")
    monkeypatch.setattr(
        "trading.core.workflow_studies.structured_qualification_runtime_contract",
        lambda _path: {
            "policy_set": {"identity": "a" * 64, "releases": []},
            "cost_policies": {},
            "evidence_contract": {},
        },
    )
    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)

    with pytest.raises(WorkflowAuthoringError, match="explicit study route"):
        studies.initialize(
            version,
            study_slug="missing-route",
            title="Missing route",
            created_by="research-agent",
        )

    study = studies.initialize(
        version,
        study_slug="clean-route",
        title="Clean route",
        created_by="research-agent",
        route="clean-historical",
    )

    metadata = read_markdown_document(study / "README.md").metadata
    assert metadata["route"] == "clean-historical"
    assert (study / "QUALIFICATION_SPEC.json").is_file()


def test_first_development_transition_requires_separate_human_authorization(
    tmp_path,
    monkeypatch,
) -> None:
    root, repository = _initialize_root(tmp_path)
    version = root / "example-workflow--v001"
    version.mkdir()
    (version / "RELEASE.json").write_text(
        json.dumps({"capabilities": ["study-time-retrospective-v1"]}) + "\n",
        encoding="utf-8",
    )
    study = version / "work" / "studies" / "example--s001"
    study.mkdir(parents=True)
    (study / "PREREGISTRATION.json").write_text("{}\n", encoding="utf-8")
    document = MarkdownDocument(
        {
            "status": "preregistered",
            "route": "study-time-retrospective",
            "preregistered_by": "owner@example.com",
        },
        "# Study\n",
    )
    studies = WorkflowStudyService(root, now=lambda: FIXED_TIME)
    monkeypatch.setattr(repository, "_require_structurally_valid", lambda: None)
    monkeypatch.setattr(studies.repository, "_require_structurally_valid", lambda: None)
    monkeypatch.setattr(studies.repository, "sync", lambda: None)
    monkeypatch.setattr(studies.repository, "_require_valid", lambda: None)
    monkeypatch.setattr(
        studies,
        "_study_context",
        lambda _path: (study, version, {"status": "active"}, document),
    )
    monkeypatch.setattr(studies, "_write_study_readme", lambda *_args: None)

    with pytest.raises(WorkflowAuthoringError, match="approved-by"):
        studies.transition(study, "running", actor="research-agent")
    with pytest.raises(WorkflowAuthoringError, match="preregistered human owner"):
        studies.transition(
            study,
            "running",
            actor="research-agent",
            approved_by="other@example.com",
        )

    studies.transition(
        study,
        "running",
        actor="research-agent",
        approved_by="owner@example.com",
    )
    authorization = json.loads(
        (study / "DEVELOPMENT_AUTHORIZATION.json").read_text(encoding="utf-8")
    )
    assert authorization["approved_by"] == "owner@example.com"
    assert authorization["authorized_operator"] == "research-agent"


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


@pytest.mark.parametrize(
    ("outcome", "disposition", "stage"),
    [
        ("pass", "retrospectively-supported", "retrospective-evaluation"),
        ("fail", "development-selection-failed", "development"),
        ("fail", "retrospective-screen-failed", "retrospective-evaluation"),
        ("indeterminate", None, "candidate-freeze"),
    ],
)
def test_study_time_retrospective_terminal_mapping(
    outcome: str,
    disposition: str | None,
    stage: str,
) -> None:
    WorkflowStudyService._validate_terminal_decision(
        route="study-time-retrospective",
        outcome=outcome,
        disposition=disposition,
        decision_stage=stage,
    )


def test_study_time_retrospective_rejects_insufficient_evidence() -> None:
    with pytest.raises(WorkflowAuthoringError, match="outcome, disposition"):
        WorkflowStudyService._validate_terminal_decision(
            route="study-time-retrospective",
            outcome="insufficient-evidence",
            disposition=None,
            decision_stage="retrospective-evaluation",
        )


@pytest.mark.parametrize(
    ("outcome", "disposition", "stage", "requires_current"),
    [
        ("pass", "retrospectively-supported", "retrospective-evaluation", False),
        ("fail", "development-selection-failed", "development", True),
        ("fail", "retrospective-screen-failed", "retrospective-evaluation", False),
        ("indeterminate", None, "candidate-freeze", False),
    ],
)
def test_every_study_time_completion_holds_study_registration_lock_through_commit(
    tmp_path,
    monkeypatch,
    outcome: str,
    disposition: str | None,
    stage: str,
    requires_current: bool,
) -> None:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "x--s001"
    study.mkdir(parents=True)
    service = WorkflowStudyService.__new__(WorkflowStudyService)
    service.repository = type(
        "RepositoryStub",
        (),
        {"_require_structurally_valid": lambda _self: None},
    )()
    document = MarkdownDocument(
        {
            "status": "awaiting-review",
            "route": "study-time-retrospective",
        },
        "body",
    )
    monkeypatch.setattr(
        service,
        "_study_context",
        lambda _path: (study, study.parents[2], {}, document),
    )
    monkeypatch.setattr(service, "_required_identity", lambda value, _label: value)
    monkeypatch.setattr(service, "_validate_terminal_decision", lambda **_kwargs: None)
    monkeypatch.setattr(
        "trading.core.workflow_studies.frozen_study_qualification_registry_path",
        lambda _path: tmp_path / "state" / "qualification.json",
    )
    held = False

    @contextmanager
    def controlled_lock(_path, _timeout):
        nonlocal held
        held = True
        try:
            yield
        finally:
            held = False

    monkeypatch.setattr("trading.core.workflow_studies.locked_file", controlled_lock)

    def complete_while_locked(**_kwargs):
        assert held is True
        assert _kwargs["require_current_registry"] is requires_current
        return {"outcome": outcome}

    monkeypatch.setattr(service, "_complete_locked", complete_while_locked)

    result = service.complete(
        study,
        outcome=outcome,
        reviewed_by="reviewer@example.com",
        disposition=disposition,
        decision_stage=stage,
    )

    assert result == {"outcome": outcome}
    assert held is False


def test_study_time_completion_rejects_untracked_terminal_evidence_before_writes(
    tmp_path,
    monkeypatch,
) -> None:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "x--s001"
    study.mkdir(parents=True)
    service = WorkflowStudyService.__new__(WorkflowStudyService)

    class RepositoryStub:
        @staticmethod
        def _validate_study_time_terminal(_metadata, _readme, issues) -> None:
            issues.append(type("Issue", (), {"message": "artifact is not in the Git index"})())

    service.repository = RepositoryStub()
    monkeypatch.setattr(
        "trading.core.workflow_studies.validate_study_time_terminal_evidence",
        lambda **_kwargs: "a" * 64,
    )

    with pytest.raises(WorkflowAuthoringError, match="before completion"):
        service._complete_locked(
            path=study,
            metadata={"route": "study-time-retrospective"},
            document=MarkdownDocument({}, "# Study\n"),
            outcome="pass",
            reviewer="reviewer@example.com",
            disposition="retrospectively-supported",
            decision_stage="retrospective-evaluation",
            require_current_registry=False,
        )

    assert not (study / "COMPLETION.json").exists()


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

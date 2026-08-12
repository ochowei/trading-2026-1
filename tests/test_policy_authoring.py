import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.cli import build_parser, main
from trading.core.policy_authoring import PolicyAuthoringError, PolicyRepository
from trading.core.workflow_authoring import (
    MarkdownDocument,
    read_markdown_document,
    render_markdown_document,
)

FIXED_TIME = datetime(2026, 8, 12, 2, 3, 4, tzinfo=UTC)


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _initialize_root(tmp_path: Path) -> tuple[Path, PolicyRepository]:
    root = tmp_path / "policies"
    _write_document(
        root / "README.md",
        {"schema_version": 1, "policies": {}},
        """# Research Policies

<!-- GENERATED:POLICY_INDEX_START -->
_No policy versions registered._
<!-- GENERATED:POLICY_INDEX_END -->
""",
    )
    return root, PolicyRepository(
        root,
        now=lambda: FIXED_TIME,
        conformance_runner=lambda _paths: None,
    )


def _register_draft(root: Path) -> Path:
    registry = read_markdown_document(root / "README.md")
    registry.metadata["policies"] = {
        "example-policy": {
            "title": "Example Policy",
            "versions": {
                "v001": {"path": "example-policy--v001", "status": "draft"},
            },
        }
    }
    _write_document(root / "README.md", registry.metadata, registry.body)
    version = root / "example-policy--v001"
    _write_document(
        version / "README.md",
        {
            "policy": "example-policy",
            "title": "Example Policy",
            "version": "v001",
            "definition": "POLICY.md",
            "config": "policy.yaml",
            "supersedes": None,
            "implementation": ["src/trading/example.py"],
            "conformance": ["tests/test_example.py"],
        },
        "# Example Policy\n",
    )
    (version / "POLICY.md").write_text(
        "# Example Policy\n\nThis policy defines one complete executable constraint.\n",
        encoding="utf-8",
    )
    (version / "policy.yaml").write_text(
        "schema_version: 1\nfamily: example-policy\nversion: v001\n",
        encoding="utf-8",
    )
    (tmp_path := root.parent / "src" / "trading").mkdir(parents=True, exist_ok=True)
    (tmp_path / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    tests = root.parent / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text(
        "def test_example():\n    assert True\n", encoding="utf-8"
    )
    return version


def _register_replacement(root: Path, *, supersedes: str | None) -> Path:
    registry = read_markdown_document(root / "README.md")
    versions = registry.metadata["policies"]["example-policy"]["versions"]
    versions["v002"] = {"path": "example-policy--v002", "status": "draft"}
    _write_document(root / "README.md", registry.metadata, registry.body)
    version = root / "example-policy--v002"
    _write_document(
        version / "README.md",
        {
            "policy": "example-policy",
            "title": "Example Policy",
            "version": "v002",
            "definition": "POLICY.md",
            "config": "policy.yaml",
            "supersedes": supersedes,
            "implementation": ["src/trading/example.py"],
            "conformance": ["tests/test_example.py"],
        },
        "# Example Policy v002\n",
    )
    (version / "POLICY.md").write_text(
        "# Example Policy v002\n\nThis replacement changes one executable constraint.\n",
        encoding="utf-8",
    )
    (version / "policy.yaml").write_text(
        "schema_version: 1\nfamily: example-policy\nversion: v002\n",
        encoding="utf-8",
    )
    return version


def test_empty_policy_registry_is_valid(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path)

    assert repository.validate_all() == ()


def test_sync_makes_a_registered_draft_valid(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path)
    _register_draft(root)

    assert any("index is stale" in issue.message for issue in repository.validate_all())

    repository.sync()

    assert repository.validate_all() == ()
    assert "example-policy--v001" in (root / "README.md").read_text(encoding="utf-8")


def test_release_pins_contract_config_implementation_and_conformance(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path)
    version = _register_draft(root)
    repository.sync()

    release = repository.release(version, approved_by="policy-owner")

    assert release["approved_at"] == "2026-08-12T02:03:04.000000Z"
    assert release["policy_sha256"]
    assert release["config_sha256"]
    assert release["implementation"][0]["sha256"]
    assert release["conformance"][0]["sha256"]
    assert json.loads((version / "RELEASE.json").read_text(encoding="utf-8")) == release
    registry = read_markdown_document(root / "README.md").metadata
    assert registry["policies"]["example-policy"]["versions"]["v001"]["status"] == "active"
    assert repository.validate_all() == ()

    (version / "policy.yaml").write_text(
        "schema_version: 1\nfamily: example-policy\nversion: v001\nchanged: true\n",
        encoding="utf-8",
    )
    assert any(
        "published policy config digest has changed" in issue.message
        for issue in repository.validate_all()
    )


def test_cli_validates_and_syncs_policy_registries_without_backdating(
    tmp_path: Path, capsys
) -> None:
    root, _repository = _initialize_root(tmp_path)

    main(["policy", "--root", str(root), "validate", "--all"])
    assert "policy validation passed" in capsys.readouterr().out
    main(["policy", "--root", str(root), "sync"])
    assert "policy indexes synchronized" in capsys.readouterr().out

    args = build_parser().parse_args(
        ["policy", "--root", str(root), "release", "example-policy--v001", "--approved-by", "owner"]
    )
    assert args.policy_command == "release"
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "policy",
                "release",
                "example-policy--v001",
                "--approved-by",
                "owner",
                "--prepared-at",
                "2020-01-01T00:00:00Z",
            ]
        )


def test_policy_version_abandon_and_retire_are_guarded(tmp_path: Path) -> None:
    root, repository = _initialize_root(tmp_path)
    draft = _register_draft(root)
    repository.sync()

    repository.transition_version(draft, "abandoned")
    registry = read_markdown_document(root / "README.md").metadata
    assert registry["policies"]["example-policy"]["versions"]["v001"]["status"] == "abandoned"

    root2, repository2 = _initialize_root(tmp_path / "second")
    active = _register_draft(root2)
    repository2.sync()
    repository2.release(active, approved_by="policy-owner")
    with pytest.raises(PolicyAuthoringError, match="requires --approved-by"):
        repository2.transition_version(active, "retired")
    repository2.transition_version(active, "retired", approved_by="policy-owner")
    assert repository2.validate_all() == ()


def test_replacement_release_requires_exact_active_supersedes_without_partial_write(
    tmp_path: Path,
) -> None:
    root, repository = _initialize_root(tmp_path)
    active = _register_draft(root)
    repository.sync()
    repository.release(active, approved_by="policy-owner")
    replacement = _register_replacement(root, supersedes=None)
    repository.sync()

    with pytest.raises(PolicyAuthoringError, match="must supersede active policy version v001"):
        repository.release(replacement, approved_by="policy-owner")

    assert not (replacement / "RELEASE.json").exists()
    registry = read_markdown_document(root / "README.md").metadata
    assert registry["policies"]["example-policy"]["versions"]["v001"]["status"] == "active"

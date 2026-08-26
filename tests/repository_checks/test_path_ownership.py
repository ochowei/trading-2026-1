import importlib.util
import json
from pathlib import Path

CHECK_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "repository-checks" / "check_path_ownership.py"
)
SPEC = importlib.util.spec_from_file_location("check_path_ownership", CHECK_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _document(*rules: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "coverage_roots": ["public"],
        "rules": list(rules),
    }


def _rule(pattern: str, **overrides: object) -> dict[str, object]:
    rule: dict[str, object] = {
        "pattern": pattern,
        "status": "active",
        "canonical_owner": "OWNER.md",
        "allows_new_content": True,
        "reason": "fixture",
    }
    rule.update(overrides)
    return rule


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "public").mkdir()
    (tmp_path / "OWNER.md").write_text("owner", encoding="utf-8")
    return tmp_path


def test_valid_registry_classifies_every_public_child(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "public" / "active.py").write_text("", encoding="utf-8")

    issues = MODULE.validate_document(
        _document(_rule("public/*.py")),
        repo_root=repo,
    )

    assert issues == []


def test_registry_rejects_unknown_status_missing_path_and_unclassified_child(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    (repo / "public" / "unowned.py").write_text("", encoding="utf-8")

    issues = MODULE.validate_document(
        _document(_rule("public/missing.py", status="mystery")),
        repo_root=repo,
    )

    assert "public/missing.py: unknown status 'mystery'" in issues
    assert "public/missing.py: required pattern matches no path" in issues
    assert "unclassified public path: public/unowned.py" in issues


def test_registry_rejects_duplicate_and_overlapping_rules(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "public" / "active.py").write_text("", encoding="utf-8")

    issues = MODULE.validate_document(
        _document(
            _rule("public/*.py"),
            _rule("public/active.py"),
            _rule("public/active.py"),
        ),
        repo_root=repo,
    )

    assert "duplicate ownership pattern: public/active.py" in issues
    assert any(issue.startswith("ambiguous ownership for public/active.py") for issue in issues)


def test_closed_directory_rejects_new_children(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    closed = repo / "public" / "legacy"
    closed.mkdir()
    (closed / "README.md").write_text("", encoding="utf-8")
    document = _document(
        _rule(
            "public/legacy",
            status="legacy-compat",
            allows_new_content=False,
            content_guard="closed-children",
            allowed_children=["README.md"],
        )
    )
    assert MODULE.validate_document(document, repo_root=repo) == []

    (closed / "new_active.py").write_text("", encoding="utf-8")

    issues = MODULE.validate_document(document, repo_root=repo)

    assert any(issue.startswith("public/legacy: closed children changed") for issue in issues)


def test_repository_registry_passes() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    registry_path = repo_root / "config" / "repository-checks" / "path-ownership.json"
    document = json.loads(registry_path.read_text(encoding="utf-8"))

    assert MODULE.validate_document(document, repo_root=repo_root) == []

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading.core.policy_authoring import PolicyRepository
from trading.core.workflow_authoring import (
    MarkdownDocument,
    render_markdown_document,
)
from trading.policies import PolicyResolutionError, PolicyResolver, PolicySet

FIXED_TIME = datetime(2026, 8, 12, 4, 5, 6, tzinfo=UTC)


def _write_document(path: Path, metadata: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_markdown_document(MarkdownDocument(metadata, body)))


def _released_policy(tmp_path: Path, family: str, values: str) -> tuple[Path, PolicyRepository]:
    root = tmp_path / "policies"
    implementation = tmp_path / "src" / "trading" / "policies" / "models.py"
    implementation.parent.mkdir(parents=True, exist_ok=True)
    implementation.write_text("POLICY_MODEL_VERSION = 1\n", encoding="utf-8")
    conformance = tmp_path / "tests" / "policies" / "test_policy_resolver.py"
    conformance.parent.mkdir(parents=True, exist_ok=True)
    conformance.write_text("def test_policy():\n    assert True\n", encoding="utf-8")
    path_name = f"{family}--v001"
    _write_document(
        root / "README.md",
        {
            "schema_version": 1,
            "policies": {
                family: {
                    "title": family,
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
    _write_document(
        version / "README.md",
        {
            "policy": family,
            "title": family,
            "version": "v001",
            "definition": "POLICY.md",
            "config": "policy.yaml",
            "supersedes": None,
            "implementation": ["src/trading/policies/models.py"],
            "conformance": ["tests/policies/test_policy_resolver.py"],
        },
        f"# {family}\n",
    )
    (version / "POLICY.md").write_text(
        f"# {family}\n\nThis released policy is complete and executable.\n",
        encoding="utf-8",
    )
    (version / "policy.yaml").write_text(
        f"schema_version: 1\nfamily: {family}\nversion: v001\nkind: test\nvalues:\n{values}",
        encoding="utf-8",
    )
    repository = PolicyRepository(
        root,
        now=lambda: FIXED_TIME,
        conformance_runner=lambda _paths: None,
    )
    repository.sync()
    repository.release(version, approved_by="policy-owner")
    return root, repository


def test_resolver_returns_only_an_exact_verified_release(tmp_path: Path) -> None:
    root, _repository = _released_policy(tmp_path, "market", "  calendar: XNYS\n")

    release = PolicyResolver(root).resolve("market", "v001")

    assert release.identity.family == "market"
    assert release.identity.version == "v001"
    assert release.values == {"calendar": "XNYS"}
    assert len(release.release_digest) == 64

    (root / "market--v001" / "policy.yaml").write_text(
        "schema_version: 1\nfamily: market\nversion: v001\nkind: test\nvalues:\n  calendar: MUTATED\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyResolutionError, match="published policy config digest has changed"):
        PolicyResolver(root).resolve("market", "v001")


def test_policy_set_rejects_duplicates_and_has_order_independent_identity(tmp_path: Path) -> None:
    market_root, _repository = _released_policy(tmp_path, "market", "  calendar: XNYS\n")
    market = PolicyResolver(market_root).resolve("market", "v001")

    broker_root, _repository = _released_policy(
        tmp_path / "broker-repo",
        "broker",
        "  order_type: stop-market\n",
    )
    broker = PolicyResolver(broker_root).resolve("broker", "v001")

    assert PolicySet((market, broker)).identity == PolicySet((broker, market)).identity
    with pytest.raises(PolicyResolutionError, match="duplicate policy family"):
        PolicySet((market, market))


def test_resolver_rejects_unknown_top_level_config_fields(tmp_path: Path) -> None:
    root, _repository = _released_policy(tmp_path, "market", "  calendar: XNYS\n")
    config = root / "market--v001" / "policy.yaml"
    config.write_text(f"{config.read_text(encoding='utf-8')}unknown: true\n", encoding="utf-8")
    release_path = root / "market--v001" / "RELEASE.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["config_sha256"] = hashlib.sha256(config.read_bytes()).hexdigest()
    release_path.write_text(json.dumps(release, sort_keys=True), encoding="utf-8")

    with pytest.raises(PolicyResolutionError, match="unknown policy config fields"):
        PolicyResolver(root).resolve("market", "v001")

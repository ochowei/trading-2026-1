import subprocess
from pathlib import Path

import pytest

from trading.policies import PolicyIdentity, PolicyRelease, PolicySet
from trading.research_data.definitions import ResearchDefinitionError, ResearchDefinitionStore


def _sources(tmp_path: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for role in ("strategy", "detector", "backtester"):
        path = tmp_path / f"{role}.py"
        path.write_text(f"ROLE = {role!r}\n", encoding="utf-8")
        paths[role] = path
    return paths


def _policy_set(config_digest: str) -> PolicySet:
    return PolicySet(
        (
            PolicyRelease(
                identity=PolicyIdentity("market", "v001"),
                kind="market",
                values={"calendar": "XNYS"},
                release_digest="a" * 64,
                config_digest=config_digest,
                path="policies/market--v001",
            ),
        )
    )


def test_definition_snapshot_identity_changes_with_selected_policy_release(tmp_path: Path) -> None:
    sources = _sources(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Policy Test",
            "-c",
            "user.email=policy@example.test",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=tmp_path,
        check=True,
    )
    store = ResearchDefinitionStore(tmp_path / "blobs")
    common = {
        "resolved_config": {"threshold": 1},
        "sources": sources,
        "execution_engine_version": "engine-v1",
        "dependency_versions": {"pandas": "2"},
        "repo_root": tmp_path,
    }

    first = store.capture(**common, policy_set=_policy_set("b" * 64))
    changed = store.capture(**common, policy_set=_policy_set("c" * 64))

    assert first.fingerprint != changed.fingerprint
    assert first.policy_set_identity == _policy_set("b" * 64).identity
    assert first.policies[0]["family"] == "market"
    assert store.load(first.blob)["policy_set"]["identity"] == first.policy_set_identity


def test_workflow_native_capture_requires_an_explicit_policy_set(tmp_path: Path) -> None:
    sources = _sources(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Policy Test",
            "-c",
            "user.email=policy@example.test",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=tmp_path,
        check=True,
    )

    with pytest.raises(ResearchDefinitionError, match="requires an explicit policy set"):
        ResearchDefinitionStore(tmp_path / "blobs").capture(
            resolved_config={"threshold": 1},
            sources=sources,
            execution_engine_version="engine-v1",
            dependency_versions={"pandas": "2"},
            repo_root=tmp_path,
            workflow_native=True,
        )

import subprocess

from trading.legacy.definition_resolver import resolve_current_definition


def test_current_definition_resolution_is_read_only(tmp_path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "baseline"],
        cwd=tmp_path,
        check=True,
    )
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source

    class SnapshotAwareStrategy:
        def capture_research_definition(self, store):
            return store.capture(
                resolved_config={"ticker": "SPY"},
                sources=sources,
                execution_engine_version="execution-v1",
                dependency_versions={"pandas": "2.3.1"},
            )

    blob_root = tmp_path / "research-data"
    definition = resolve_current_definition(
        "spy_001",
        experiment_loader=lambda _name: SnapshotAwareStrategy(),
        blob_root=blob_root,
    )

    assert definition is not None
    assert len(definition.fingerprint) == 64
    assert not blob_root.exists()


def test_legacy_experiment_has_no_current_definition_snapshot(tmp_path) -> None:
    definition = resolve_current_definition(
        "spy_legacy",
        experiment_loader=lambda _name: object(),
        blob_root=tmp_path / "research-data",
    )

    assert definition is None

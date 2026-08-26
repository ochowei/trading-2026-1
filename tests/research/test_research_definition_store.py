import hashlib
import json
import subprocess

import pytest

from trading.core.sleeve_engine import ExecutionCostPolicy
from trading.research_data import (
    DefinitionBlobRef,
    ImmutableBlobCorruptionError,
    ResearchDefinitionError,
    ResearchDefinitionStore,
)


def initialize_repository(path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-qm", "baseline"], cwd=path, check=True)


def test_definition_requires_all_outcome_relevant_source_roles(tmp_path) -> None:
    detector = tmp_path / "detector.py"
    detector.write_text("def signal():\n    return True\n", encoding="utf-8")

    with pytest.raises(ResearchDefinitionError, match="strategy, detector, and backtester"):
        ResearchDefinitionStore(tmp_path / "research-data").capture(
            resolved_config={"ticker": "SPY"},
            sources={"detector": detector},
            execution_engine_version="execution-v1",
            dependency_versions={"pandas": "2.3.1"},
        )


def test_definition_capture_requires_reconstructable_git_context(tmp_path) -> None:
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source

    with pytest.raises(ResearchDefinitionError, match="Git context"):
        ResearchDefinitionStore(tmp_path / "research-data").capture(
            resolved_config={"ticker": "SPY"},
            sources=sources,
            execution_engine_version="execution-v1",
            dependency_versions={"pandas": "2.3.1"},
        )


def test_definition_preview_computes_identity_without_publishing_a_blob(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    store = ResearchDefinitionStore(tmp_path / "research-data", publish=False)

    preview = store.capture(
        resolved_config={"ticker": "SPY"},
        sources=sources,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
    )

    assert len(preview.fingerprint) == 64
    assert not store.definition_blob_path(preview.blob.digest).exists()


def test_semantic_fingerprint_ignores_formatting_but_changes_with_threshold(tmp_path) -> None:
    initialize_repository(tmp_path)
    source = tmp_path / "detector.py"
    strategy = tmp_path / "strategy.py"
    backtester = tmp_path / "backtester.py"
    strategy.write_text("class Strategy:\n    pass\n", encoding="utf-8")
    backtester.write_text("class Backtester:\n    pass\n", encoding="utf-8")
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY", "lookback": 20},
        "sources": {
            "strategy": strategy,
            "detector": source,
            "backtester": backtester,
        },
        "execution_engine_version": "execution-v1",
        "dependency_versions": {"pandas": "2.3.1"},
    }
    source.write_text(
        "# first comment\ndef signal(value):\n    return value > 0.20\n",
        encoding="utf-8",
    )
    first = store.capture(**common)
    source.write_text(
        "def signal( value ):\n\n    # different comment\n    return value>0.20\n",
        encoding="utf-8",
    )
    formatting_only = store.capture(**common)
    source.write_text(
        "def signal(value):\n    return value > 0.25\n",
        encoding="utf-8",
    )
    changed_threshold = store.capture(**common)

    assert formatting_only.fingerprint == first.fingerprint
    assert formatting_only.blob.digest != first.blob.digest
    assert changed_threshold.fingerprint != first.fingerprint


def test_semantic_fingerprint_ignores_reporting_only_method_changes(tmp_path) -> None:
    initialize_repository(tmp_path)
    detector = tmp_path / "detector.py"
    strategy = tmp_path / "strategy.py"
    backtester = tmp_path / "backtester.py"
    detector.write_text("def signal(value):\n    return value > 0.20\n", encoding="utf-8")
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return value\n"
        "\n"
        "    def render_report(self, value):\n"
        "        return f'report {value}'\n",
        encoding="utf-8",
    )
    backtester.write_text("class Backtester:\n    pass\n", encoding="utf-8")
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": {
            "strategy": strategy,
            "detector": detector,
            "backtester": backtester,
        },
        "reporting_only_symbols": {"strategy": ("render_report",)},
        "execution_engine_version": "execution-v1",
        "dependency_versions": {"pandas": "2.3.1"},
    }

    first = store.capture(**common)
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return value\n"
        "\n"
        "    def render_report(self, value):\n"
        "        return f'changed display {value}'\n",
        encoding="utf-8",
    )
    reporting_only = store.capture(**common)

    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return value + 1\n"
        "\n"
        "    def render_report(self, value):\n"
        "        return f'changed display {value}'\n",
        encoding="utf-8",
    )
    behavior_changed = store.capture(**common)

    assert reporting_only.fingerprint == first.fingerprint
    assert reporting_only.blob.digest != first.blob.digest
    assert behavior_changed.fingerprint != first.fingerprint


def test_reporting_named_method_remains_semantic_without_explicit_declaration(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(
            "def render_report(value):\n    return value\n"
            if role == "strategy"
            else "class Component:\n    pass\n",
            encoding="utf-8",
        )
        sources[role] = source
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": sources,
        "execution_engine_version": "execution-v1",
        "dependency_versions": {"pandas": "2.3.1"},
    }

    first = store.capture(**common)
    sources["strategy"].write_text(
        "def render_report(value):\n    return value + 1\n", encoding="utf-8"
    )
    changed = store.capture(**common)

    assert changed.fingerprint != first.fingerprint


def test_declared_reporting_method_remains_semantic_when_outcome_code_references_it(
    tmp_path,
) -> None:
    initialize_repository(tmp_path)
    strategy = tmp_path / "strategy.py"
    detector = tmp_path / "detector.py"
    backtester = tmp_path / "backtester.py"
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return self.render_report(value)\n"
        "\n"
        "    def render_report(self, value):\n"
        "        return value\n",
        encoding="utf-8",
    )
    detector.write_text("class Detector:\n    pass\n", encoding="utf-8")
    backtester.write_text("class Backtester:\n    pass\n", encoding="utf-8")
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": {
            "strategy": strategy,
            "detector": detector,
            "backtester": backtester,
        },
        "reporting_only_symbols": {"strategy": ("render_report",)},
        "execution_engine_version": "execution-v1",
        "dependency_versions": {"pandas": "2.3.1"},
    }

    first = store.capture(**common)
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return self.render_report(value)\n"
        "\n"
        "    def render_report(self, value):\n"
        "        return value + 1\n",
        encoding="utf-8",
    )
    changed = store.capture(**common)

    assert changed.fingerprint != first.fingerprint


def test_transitive_declared_reporting_dependency_remains_semantic(tmp_path) -> None:
    initialize_repository(tmp_path)
    strategy = tmp_path / "strategy.py"
    detector = tmp_path / "detector.py"
    backtester = tmp_path / "backtester.py"
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return self.report(value)\n"
        "\n"
        "    def report(self, value):\n"
        "        return self.format_report(value)\n"
        "\n"
        "    def format_report(self, value):\n"
        "        return value\n",
        encoding="utf-8",
    )
    detector.write_text("class Detector:\n    pass\n", encoding="utf-8")
    backtester.write_text("class Backtester:\n    pass\n", encoding="utf-8")
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": {
            "strategy": strategy,
            "detector": detector,
            "backtester": backtester,
        },
        "reporting_only_symbols": {"strategy": ("report", "format_report")},
        "execution_engine_version": "execution-v1",
        "dependency_versions": {"pandas": "2.3.1"},
    }

    first = store.capture(**common)
    strategy.write_text(
        "class Strategy:\n"
        "    def execute(self, value):\n"
        "        return self.report(value)\n"
        "\n"
        "    def report(self, value):\n"
        "        return self.format_report(value)\n"
        "\n"
        "    def format_report(self, value):\n"
        "        return value + 1\n",
        encoding="utf-8",
    )
    changed = store.capture(**common)

    assert changed.fingerprint != first.fingerprint


def test_engine_and_dependency_identity_change_semantic_fingerprint(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": sources,
    }

    baseline = store.capture(
        **common,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
    )
    changed_engine = store.capture(
        **common,
        execution_engine_version="execution-v2",
        dependency_versions={"pandas": "2.3.1"},
    )
    changed_dependency = store.capture(
        **common,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.4.0"},
    )

    assert changed_engine.fingerprint != baseline.fingerprint
    assert changed_dependency.fingerprint != baseline.fingerprint


def test_base_and_stress_cost_assumptions_are_part_of_definition_identity(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    store = ResearchDefinitionStore(tmp_path / "research-data")
    common = {
        "resolved_config": {"ticker": "SPY"},
        "sources": sources,
        "execution_engine_version": "canonical-sleeve-v1",
        "dependency_versions": {"pandas": "2.3.1"},
        "base_cost_policy": ExecutionCostPolicy(5.0, 5.0, 1.0),
    }

    baseline = store.capture(
        **common,
        stress_cost_policy=ExecutionCostPolicy(20.0, 20.0, 2.0),
    )
    changed_stress = store.capture(
        **common,
        stress_cost_policy=ExecutionCostPolicy(30.0, 30.0, 2.0),
    )
    restored = store.load(baseline.blob)

    assert changed_stress.fingerprint != baseline.fingerprint
    assert restored["execution_cost_policies"]["base"]["entry_slippage_bps"] == 5.0
    assert restored["execution_cost_policies"]["stress"]["exit_slippage_bps"] == 20.0


def test_definition_rejects_non_adverse_stress_cost_policy(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source

    with pytest.raises(ResearchDefinitionError, match="stress cost policy"):
        ResearchDefinitionStore(tmp_path / "research-data").capture(
            resolved_config={"ticker": "SPY"},
            sources=sources,
            execution_engine_version="canonical-sleeve-v1",
            dependency_versions={"pandas": "2.3.1"},
            base_cost_policy=ExecutionCostPolicy(10.0, 10.0, 2.0),
            stress_cost_policy=ExecutionCostPolicy(5.0, 20.0, 2.0),
        )


def test_dirty_worktree_definition_blob_restores_exact_sources_and_git_context(tmp_path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repository, check=True)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = repository / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=repository, check=True)
    dirty_content = "def signal(value):\n    return value > 0.25\n"
    sources["detector"].write_text(dirty_content, encoding="utf-8")
    store = ResearchDefinitionStore(tmp_path / "research-data")

    snapshot = store.capture(
        resolved_config={"ticker": "SPY"},
        sources=sources,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
        repo_root=repository,
    )
    restored = store.load(snapshot.blob)

    assert restored["sources"]["detector"] == dirty_content
    assert restored["git_context"]["dirty"] is True
    assert "detector.py" in restored["git_context"]["status"]
    assert "0.25" in restored["git_context"]["diff"]


def test_definition_load_recomputes_semantic_fingerprint(tmp_path) -> None:
    initialize_repository(tmp_path)
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = tmp_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    store = ResearchDefinitionStore(tmp_path / "research-data")
    captured = store.capture(
        resolved_config={"ticker": "SPY"},
        sources=sources,
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
    )
    payload = store.load(captured.blob)
    payload["fingerprint"] = "0" * 64
    forged = (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
    digest = hashlib.sha256(forged).hexdigest()
    reference = DefinitionBlobRef(
        digest=digest,
        byte_count=len(forged),
        fingerprint="0" * 64,
    )
    forged_path = store.definition_blob_path(digest)
    forged_path.parent.mkdir(parents=True, exist_ok=True)
    forged_path.write_bytes(forged)

    with pytest.raises(ImmutableBlobCorruptionError, match="semantic fingerprint"):
        store.load(reference)

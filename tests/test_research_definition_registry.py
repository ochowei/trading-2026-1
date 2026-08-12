from pathlib import Path

import pytest

from trading.research_definitions import (
    ResearchDefinitionRegistry,
    ResearchDefinitionRegistryError,
)


def _definition(root: Path, family: str, trial: str) -> None:
    path = root / family / trial
    path.mkdir(parents=True)
    (path / "definition.py").write_text("DEFINITION = 1\n", encoding="utf-8")


def test_workflow_native_registry_discovers_family_scoped_trials(tmp_path: Path) -> None:
    root = tmp_path / "research_definitions"
    _definition(root, "trend-pullback", "trial-001")
    _definition(root, "trend-pullback", "trial-002")

    registry = ResearchDefinitionRegistry(root)

    assert registry.list_trials() == (
        "trend-pullback/trial-001",
        "trend-pullback/trial-002",
    )
    assert registry.resolve("trend-pullback/trial-001").name == "definition.py"


def test_workflow_native_registry_rejects_legacy_or_ambiguous_identity(tmp_path: Path) -> None:
    registry = ResearchDefinitionRegistry(tmp_path / "research_definitions")

    with pytest.raises(ResearchDefinitionRegistryError, match="family/trial"):
        registry.resolve("spy_007")
    with pytest.raises(ResearchDefinitionRegistryError, match="lowercase kebab-case"):
        registry.resolve("SPY/trial_001")

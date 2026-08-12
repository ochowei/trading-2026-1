"""Registry for workflow-native research-definition source identities."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ResearchDefinitionRegistryError(ValueError):
    """A workflow-native research-definition identity is invalid or missing."""


class ResearchDefinitionRegistry:
    """Discover explicit family/trial source identities outside legacy experiments."""

    def __init__(self, root: Path = Path("src/trading/research_definitions")) -> None:
        self.root = Path(root)

    def list_trials(self) -> tuple[str, ...]:
        """Return every definition.py-backed family/trial identity."""
        if not self.root.is_dir():
            return ()
        return tuple(
            sorted(
                f"{path.parent.parent.name}/{path.parent.name}"
                for path in self.root.glob("*/*/definition.py")
                if _SLUG.fullmatch(path.parent.parent.name) and _SLUG.fullmatch(path.parent.name)
            )
        )

    def resolve(self, identity: str) -> Path:
        """Resolve one exact family/trial identity to its source entry point."""
        parts = identity.split("/")
        if len(parts) != 2:
            raise ResearchDefinitionRegistryError(
                "research definition identity must be family/trial"
            )
        if any(_SLUG.fullmatch(part) is None for part in parts):
            raise ResearchDefinitionRegistryError(
                "research definition names must use lowercase kebab-case"
            )
        path = self.root / parts[0] / parts[1] / "definition.py"
        if not path.is_file():
            raise ResearchDefinitionRegistryError(f"unknown research definition: {identity}")
        return path

    def load(self, identity: str) -> object:
        """Load one explicit definition object without legacy auto-discovery."""
        path = self.resolve(identity)
        module_name = "trading_research_definition_" + identity.replace("/", "_").replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ResearchDefinitionRegistryError(f"cannot load research definition: {identity}")
        module = importlib.util.module_from_spec(spec)
        self._execute_module(spec.loader, module, identity)
        definition = getattr(module, "DEFINITION", None)
        if definition is None:
            raise ResearchDefinitionRegistryError(
                f"research definition has no DEFINITION object: {identity}"
            )
        return definition

    @staticmethod
    def _execute_module(loader: object, module: ModuleType, identity: str) -> None:
        execute = getattr(loader, "exec_module", None)
        if not callable(execute):
            raise ResearchDefinitionRegistryError(f"cannot load research definition: {identity}")
        try:
            execute(module)
        except Exception as exc:
            raise ResearchDefinitionRegistryError(
                f"cannot load research definition {identity}: {exc}"
            ) from exc

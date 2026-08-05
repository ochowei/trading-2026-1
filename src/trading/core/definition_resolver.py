"""Read-only resolution of the current semantic research definition."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from trading.experiments import get_experiment
from trading.research_data import (
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)


class ExperimentLoader(Protocol):
    def __call__(self, name: str) -> object: ...


def resolve_current_definition(
    experiment_name: str,
    *,
    experiment_loader: ExperimentLoader = get_experiment,
    blob_root: Path = Path(".research-data/blobs"),
) -> ResearchDefinitionSnapshot | None:
    """Compute current definition identity without publishing immutable state."""
    try:
        strategy = experiment_loader(experiment_name)
    except KeyError:
        return None
    capture = getattr(strategy, "capture_research_definition", None)
    if not callable(capture):
        return None
    captured = capture(ResearchDefinitionStore(blob_root, publish=False))
    if not isinstance(captured, ResearchDefinitionSnapshot):
        raise TypeError("capture_research_definition must return ResearchDefinitionSnapshot")
    return captured


def resolve_current_definition_fingerprint(experiment_name: str) -> str | None:
    """Return the current semantic fingerprint for result-validity consumers."""
    definition = resolve_current_definition(experiment_name)
    return definition.fingerprint if definition is not None else None

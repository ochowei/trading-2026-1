"""Verified workflow and policy binding for workflow-native research definitions."""

from __future__ import annotations

from pathlib import Path

from trading.core.workflow_authoring import WorkflowRepository, read_markdown_document
from trading.policies import PolicyResolver, PolicySet


class WorkflowNativeExecutionError(ValueError):
    """A definition cannot be bound to an exact released workflow and policy set."""


def resolve_workflow_policy_set(version_path: Path) -> PolicySet:
    """Resolve the four exact policy pins of one valid released workflow version."""
    path = Path(version_path).resolve()
    if not (path / "README.md").is_file() or not (path / "RELEASE.json").is_file():
        raise WorkflowNativeExecutionError("workflow version is not a released version directory")
    repository = WorkflowRepository(path.parent)
    issues = repository.validate_path(path)
    if issues:
        raise WorkflowNativeExecutionError(str(issues[0]))
    raw_pins = read_markdown_document(path / "README.md").metadata.get("policies")
    if not isinstance(raw_pins, list) or len(raw_pins) != 4:
        raise WorkflowNativeExecutionError("workflow must pin exactly four policy families")
    resolver = PolicyResolver(path.parent.parent / "policies")
    releases = []
    for pin in raw_pins:
        if not isinstance(pin, dict):
            raise WorkflowNativeExecutionError("workflow policy pin is malformed")
        try:
            family = str(pin["family"])
            version = str(pin["version"])
            expected_path = str(pin["path"])
            expected_digest = str(pin["release_digest"])
        except KeyError as exc:
            raise WorkflowNativeExecutionError("workflow policy pin is incomplete") from exc
        release = resolver.resolve(family, version)
        if release.path != expected_path or release.release_digest != expected_digest:
            raise WorkflowNativeExecutionError(f"workflow policy pin drift: {family}@{version}")
        releases.append(release)
    return PolicySet(tuple(releases))

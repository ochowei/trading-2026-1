"""Verified workflow and policy binding for workflow-native research definitions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from trading.policies import PolicyResolver, PolicySet
from trading.workflow.authoring import WorkflowRepository, read_markdown_document


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
    _registry, workflow, version, record = repository._registered_version(path)
    if record.get("status") == "prepared":
        raise WorkflowNativeExecutionError(f"workflow version is not active: {workflow}@{version}")
    return resolve_workflow_policy_set_from_release(path)


def resolve_workflow_policy_set_from_release(version_path: Path) -> PolicySet:
    """Resolve exact policy pins without recursively validating the workflow's studies."""
    path = Path(version_path).resolve()
    readme_path = path / "README.md"
    release_path = path / "RELEASE.json"
    definition_path = path / "WORKFLOW.md"
    if not readme_path.is_file() or not release_path.is_file() or not definition_path.is_file():
        raise WorkflowNativeExecutionError("workflow version is not a released version directory")
    metadata = read_markdown_document(readme_path).metadata
    try:
        release = json.loads(release_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowNativeExecutionError(f"workflow release is unreadable: {exc}") from exc
    if not isinstance(release, dict) or release.get("schema_version") != 1:
        raise WorkflowNativeExecutionError("workflow release is malformed")
    if release.get("workflow") != metadata.get("workflow") or release.get(
        "version"
    ) != metadata.get("version"):
        raise WorkflowNativeExecutionError("workflow release identity differs from README")
    workflow_digest = hashlib.sha256(definition_path.read_bytes()).hexdigest()
    if release.get("workflow_sha256") != workflow_digest:
        raise WorkflowNativeExecutionError("released workflow definition digest has changed")
    raw_pins = metadata.get("policies")
    if not isinstance(raw_pins, list) or len(raw_pins) != 4:
        raise WorkflowNativeExecutionError("workflow must pin exactly four policy families")
    if release.get("policies") != raw_pins:
        raise WorkflowNativeExecutionError("workflow release policy pins differ from README")
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

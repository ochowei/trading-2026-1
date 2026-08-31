"""Read-only A1-2 control-state evaluation for one exact workflow version."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading.workflow.authoring import (
    STUDY_DIRECTORY_PATTERN,
    WORKFLOW_SAFETY_CAPABILITY,
    WorkflowAuthoringError,
    WorkflowRepository,
    read_markdown_document,
)

_TERMINAL_STUDY_STATUSES = frozenset({"completed", "cancelled"})
_OUTSIDE_A1_2_STATUSES = frozenset({"superseded", "retired", "abandoned"})


@dataclass(frozen=True)
class WorkflowControlStateResult:
    """One fail-closed result for an exact workflow-version query."""

    workflow: str | None
    version: str | None
    path: str
    result: str
    control_state: str | None
    registry_status: str | None
    unfinished_study_count: int | None = None
    safety_assessment: str | None = None
    reasons: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return the stable schema-1 machine-readable representation."""
        return {
            "schema_version": 1,
            "workflow": self.workflow,
            "version": self.version,
            "path": self.path,
            "result": self.result,
            "control_state": self.control_state,
            "registry_status": self.registry_status,
            "unfinished_study_count": self.unfinished_study_count,
            "safety_assessment": self.safety_assessment,
            "reasons": list(self.reasons),
            "issues": list(self.issues),
        }


def evaluate_workflow_control_state(
    repository: WorkflowRepository,
    version_path: Path,
) -> WorkflowControlStateResult:
    """Determine N02-N06 for one exact version, or return a fail-closed result."""
    try:
        path = repository._resolve_input(version_path)
        canonical_path = repository._repo_relative(path)
        _registry, workflow, version, record = repository._registered_version(path)
    except WorkflowAuthoringError as exc:
        return WorkflowControlStateResult(
            workflow=None,
            version=None,
            path=str(version_path),
            result="invalid",
            control_state=None,
            registry_status=None,
            reasons=("exact-version-identity-invalid",),
            issues=(str(exc),),
        )

    validation_issues = repository.validate_all()
    if validation_issues:
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="invalid",
            control_state=None,
            registry_status=_string_or_none(record.get("status")),
            reasons=("repository-validation-failed",),
            issues=tuple(str(issue) for issue in validation_issues),
        )

    status = str(record.get("status"))
    if status == "draft":
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="determined",
            control_state="N02",
            registry_status=status,
            reasons=("registered-draft",),
        )
    if status == "prepared":
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="determined",
            control_state="N03",
            registry_status=status,
            reasons=("prepared-awaiting-activation",),
        )
    if status in _OUTSIDE_A1_2_STATUSES:
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="outside-a1-2",
            control_state=None,
            registry_status=status,
            reasons=("terminal-registry-status",),
        )
    if status != "active":
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="invalid",
            control_state=None,
            registry_status=status,
            reasons=("unsupported-registry-status",),
            issues=(f"unsupported workflow registry status: {status}",),
        )

    release = repository._read_json_object(path / "RELEASE.json", label="workflow release")
    capabilities = release.get("capabilities", [])
    if WORKFLOW_SAFETY_CAPABILITY not in capabilities:
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="indeterminate",
            control_state=None,
            registry_status=status,
            reasons=("safety-capability-unavailable",),
        )

    assessment = repository._open_safety_assessment_for(path)
    if assessment is not None:
        return WorkflowControlStateResult(
            workflow=workflow,
            version=version,
            path=canonical_path,
            result="determined",
            control_state="N06",
            registry_status=status,
            safety_assessment=repository._repo_relative(assessment),
            reasons=("open-safety-assessment",),
        )

    unfinished = _unfinished_study_count(path)
    return WorkflowControlStateResult(
        workflow=workflow,
        version=version,
        path=canonical_path,
        result="determined",
        control_state="N04" if unfinished == 0 else "N05",
        registry_status=status,
        unfinished_study_count=unfinished,
        reasons=("no-unfinished-studies" if unfinished == 0 else "unfinished-studies-present",),
    )


def _unfinished_study_count(version_path: Path) -> int:
    studies = version_path / "work" / "studies"
    if not studies.is_dir():
        return 0
    unfinished = 0
    for study in sorted(path for path in studies.iterdir() if path.is_dir()):
        if STUDY_DIRECTORY_PATTERN.fullmatch(study.name) is None:
            continue
        metadata = read_markdown_document(study / "README.md").metadata
        if metadata.get("status") not in _TERMINAL_STUDY_STATUSES:
            unfinished += 1
    return unfinished


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None

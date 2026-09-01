"""Authority boundary for append-only qualification-plan abandonment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from trading.core.qualification import QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY
from trading.workflow.authoring import WorkflowAuthoringError, WorkflowRepository, _sha256


@dataclass(frozen=True, slots=True)
class QualificationPlanAbandonmentAuthority:
    """Exact active workflow release that authorizes one abandonment command."""

    workflow: str
    workflow_version: str
    workflow_path: str
    workflow_release_sha256: str
    capability: str = QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY

    def as_payload(self) -> dict[str, str]:
        """Return the canonical registry payload representation."""
        return asdict(self)


def resolve_qualification_plan_abandonment_authority(
    workflow_path: Path,
    *,
    workflow_root: Path = Path("workflows"),
) -> QualificationPlanAbandonmentAuthority:
    """Resolve and verify the effective workflow release authorizing abandonment."""
    repository = WorkflowRepository(workflow_root)
    repository._require_structurally_valid()
    resolved = repository._resolve_input(workflow_path)
    repository.require_effective_version(resolved)
    _registry, workflow, version, _record = repository._registered_version(resolved)
    release_path = resolved / "RELEASE.json"
    release = repository._read_json_object(release_path, label="workflow release")
    capabilities = release.get("capabilities")
    if (
        not isinstance(capabilities, list)
        or QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY not in capabilities
    ):
        raise WorkflowAuthoringError(
            "effective workflow release does not authorize qualification-plan abandonment"
        )
    return QualificationPlanAbandonmentAuthority(
        workflow=workflow,
        workflow_version=version,
        workflow_path=repository._repo_relative(resolved),
        workflow_release_sha256=_sha256(release_path),
    )

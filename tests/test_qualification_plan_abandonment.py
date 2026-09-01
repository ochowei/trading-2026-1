from pathlib import Path

import pytest

from trading.workflow.authoring import WorkflowAuthoringError
from trading.workflow.qualification_plan_abandonment import (
    QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY,
    resolve_qualification_plan_abandonment_authority,
)


class _FakeWorkflowRepository:
    capabilities = [QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY]
    structurally_validated = False
    effective_version_required = False

    def __init__(self, root: Path) -> None:
        self.root = root

    def _require_structurally_valid(self) -> None:
        type(self).structurally_validated = True

    def _resolve_input(self, path: Path) -> Path:
        return path

    def require_effective_version(self, _path: Path) -> None:
        type(self).effective_version_required = True

    def _registered_version(self, _path: Path):
        return {}, "strategy-forward-replication-research", "v010", {"status": "active"}

    def _read_json_object(self, _path: Path, *, label: str):
        assert label == "workflow release"
        return {"capabilities": type(self).capabilities}

    def _repo_relative(self, _path: Path) -> str:
        return "workflows/strategy-forward-replication-research--v010"


def test_plan_abandonment_authority_requires_effective_capability(
    tmp_path,
    monkeypatch,
) -> None:
    version_path = tmp_path / "strategy-forward-replication-research--v010"
    version_path.mkdir()
    (version_path / "RELEASE.json").write_text("{}", encoding="utf-8")
    _FakeWorkflowRepository.capabilities = [QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY]
    _FakeWorkflowRepository.structurally_validated = False
    _FakeWorkflowRepository.effective_version_required = False
    monkeypatch.setattr(
        "trading.workflow.qualification_plan_abandonment.WorkflowRepository",
        _FakeWorkflowRepository,
    )

    authority = resolve_qualification_plan_abandonment_authority(
        version_path,
        workflow_root=tmp_path,
    )

    assert _FakeWorkflowRepository.structurally_validated
    assert _FakeWorkflowRepository.effective_version_required
    assert authority.workflow_version == "v010"
    assert authority.capability == QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY
    assert len(authority.workflow_release_sha256) == 64


def test_plan_abandonment_authority_rejects_release_without_capability(
    tmp_path,
    monkeypatch,
) -> None:
    version_path = tmp_path / "strategy-forward-replication-research--v009"
    version_path.mkdir()
    (version_path / "RELEASE.json").write_text("{}", encoding="utf-8")
    _FakeWorkflowRepository.capabilities = []
    monkeypatch.setattr(
        "trading.workflow.qualification_plan_abandonment.WorkflowRepository",
        _FakeWorkflowRepository,
    )

    with pytest.raises(WorkflowAuthoringError, match="does not authorize"):
        resolve_qualification_plan_abandonment_authority(
            version_path,
            workflow_root=tmp_path,
        )

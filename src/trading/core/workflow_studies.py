"""Guarded lifecycle operations for studies pinned to released workflows."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from trading.core.accounting import canonical_json_bytes, timestamp_text
from trading.core.workflow_authoring import (
    SLUG_PATTERN,
    STUDY_DIRECTORY_PATTERN,
    STUDY_OUTCOMES,
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    _atomic_write,
    _is_substantive,
    _sha256,
    read_markdown_document,
    render_markdown_document,
)

_STUDY_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"cancelled"}),
    "preregistered": frozenset({"running", "cancelled"}),
    "running": frozenset({"paused", "awaiting-review", "cancelled"}),
    "paused": frozenset({"running", "cancelled"}),
    "awaiting-review": frozenset({"running"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
}


class WorkflowStudyService:
    """Create and transition one auditable workflow study at a time."""

    def __init__(
        self,
        root: Path = Path("workflows"),
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = WorkflowRepository(root, now=now)
        self.root = root
        self.repo_root = root.parent

    def initialize(
        self,
        version_path: Path,
        *,
        study_slug: str,
        title: str,
        created_by: str,
        revisits: str | None = None,
    ) -> Path:
        """Create the next local study draft under an active workflow version."""
        self.repository._require_structurally_valid()
        version_resolved = self.repository._resolve_input(version_path)
        _registry, workflow, version, record = self.repository._registered_version(version_resolved)
        if record.get("status") != "active":
            raise WorkflowAuthoringError("new studies require an active workflow version")
        if not SLUG_PATTERN.fullmatch(study_slug):
            raise WorkflowAuthoringError("study slug must be lowercase kebab-case")
        title_text = self._required_identity(title, "study title")
        creator = self._required_identity(created_by, "created-by")
        revisits_path = self._normalize_revisits(revisits)

        studies_root = version_resolved / "work" / "studies"
        studies_root.mkdir(parents=True, exist_ok=True)
        number = self._next_study_number(studies_root)
        study_id = f"S{number:03d}"
        target = studies_root / f"{study_slug}--s{number:03d}"
        if target.exists():
            raise WorkflowAuthoringError(f"study path already exists: {target}")

        created_at = timestamp_text(self.repository._current_time())
        metadata: dict[str, Any] = {
            "id": study_id,
            "title": title_text,
            "workflow": workflow,
            "workflow_version": version,
            "status": "draft",
            "outcome": None,
            "created_at": created_at,
            "created_by": creator,
            "status_changed_at": None,
            "status_changed_by": None,
            "status_reason": None,
            "preregistered_at": None,
            "preregistered_by": None,
            "completed_at": None,
            "reviewed_by": None,
            "revisits": revisits_path,
        }
        files = {
            "README.md": render_markdown_document(
                MarkdownDocument(
                    metadata,
                    self._study_readme_body(title_text, workflow, version),
                )
            ),
            "HYPOTHESIS.md": self._hypothesis_template(title_text).encode(),
            "PLAN.md": self._plan_template(title_text).encode(),
            "EVIDENCE.md": self._evidence_template(title_text).encode(),
            "CONCLUSION.md": self._conclusion_template(title_text).encode(),
        }
        temporary = Path(tempfile.mkdtemp(prefix=".study-", dir=studies_root))
        try:
            for filename, content in files.items():
                _atomic_write(temporary / filename, content)
            try:
                os.rename(temporary, target)
            except FileExistsError as exc:
                raise WorkflowAuthoringError(f"study path already exists: {target}") from exc
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)

        self.repository.sync()
        self.repository._require_valid()
        return target

    def preregister(self, study_path: Path, *, approved_by: str) -> dict[str, Any]:
        """Freeze hypothesis and plan with current-time human approval evidence."""
        self.repository._require_structurally_valid()
        path, version_path, version_record, document = self._study_context(study_path)
        metadata = copy.deepcopy(document.metadata)
        if metadata.get("status") != "draft":
            raise WorkflowAuthoringError("only a draft study may be preregistered")
        if version_record.get("status") != "active":
            raise WorkflowAuthoringError("only an active workflow version may preregister a study")
        approver = self._required_identity(approved_by, "approved-by")
        for filename in ("HYPOTHESIS.md", "PLAN.md"):
            if not _is_substantive(path / filename):
                raise WorkflowAuthoringError(f"{filename} must be complete before preregistration")
        registration_path = path / "PREREGISTRATION.json"
        if registration_path.exists():
            raise WorkflowAuthoringError("draft study already has preregistration evidence")

        release_path = version_path / "RELEASE.json"
        try:
            release = json.loads(release_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkflowAuthoringError(f"cannot read workflow release: {exc}") from exc
        workflow_digest = release.get("workflow_sha256") if isinstance(release, dict) else None
        if not isinstance(workflow_digest, str):
            raise WorkflowAuthoringError("workflow release digest is missing")

        occurred_at = timestamp_text(self.repository._current_time())
        registration: dict[str, Any] = {
            "schema_version": 1,
            "study_id": metadata.get("id"),
            "workflow": metadata.get("workflow"),
            "workflow_version": metadata.get("workflow_version"),
            "study_path": self._repo_relative(path),
            "approved_at": occurred_at,
            "approved_by": approver,
            "workflow_sha256": workflow_digest,
            "hypothesis_sha256": _sha256(path / "HYPOTHESIS.md"),
            "plan_sha256": _sha256(path / "PLAN.md"),
            "revisits": metadata.get("revisits"),
        }
        metadata["status"] = "preregistered"
        metadata["status_changed_at"] = occurred_at
        metadata["status_changed_by"] = approver
        metadata["status_reason"] = None
        metadata["preregistered_at"] = occurred_at
        metadata["preregistered_by"] = approver

        _atomic_write(registration_path, canonical_json_bytes(registration), replace=False)
        self._write_study_readme(path, metadata, document.body)
        self.repository.sync()
        self.repository._require_valid()
        return registration

    def transition(
        self,
        study_path: Path,
        target_status: str,
        *,
        actor: str,
        reason: str | None = None,
    ) -> None:
        """Apply one legal non-completion study transition."""
        self.repository._require_structurally_valid()
        path, _version_path, version_record, document = self._study_context(study_path)
        metadata = copy.deepcopy(document.metadata)
        current = metadata.get("status")
        if not isinstance(current, str) or target_status not in _STUDY_TRANSITIONS.get(
            current, frozenset()
        ):
            raise WorkflowAuthoringError(f"illegal study transition: {current} -> {target_status}")
        actor_text = self._required_identity(actor, "by")
        reason_text = reason.strip() if isinstance(reason, str) and reason.strip() else None
        if target_status in {"paused", "cancelled"} and reason_text is None:
            raise WorkflowAuthoringError(f"{target_status} transition requires --reason")
        if current == "awaiting-review" and target_status == "running" and reason_text is None:
            raise WorkflowAuthoringError("returning from review requires --reason")
        if target_status == "running" and version_record.get("status") != "active":
            raise WorkflowAuthoringError("only an active workflow version may start or resume work")
        if target_status == "awaiting-review" and not _is_substantive(path / "EVIDENCE.md"):
            raise WorkflowAuthoringError("EVIDENCE.md must be complete before review")

        metadata["status"] = target_status
        metadata["status_changed_at"] = timestamp_text(self.repository._current_time())
        metadata["status_changed_by"] = actor_text
        metadata["status_reason"] = reason_text
        self._write_study_readme(path, metadata, document.body)
        self.repository.sync()
        self.repository._require_valid()

    def complete(
        self,
        study_path: Path,
        *,
        outcome: str,
        reviewed_by: str,
    ) -> dict[str, Any]:
        """Freeze an independently reviewed conclusion and terminal outcome."""
        self.repository._require_structurally_valid()
        path, _version_path, _record, document = self._study_context(study_path)
        metadata = copy.deepcopy(document.metadata)
        if metadata.get("status") != "awaiting-review":
            raise WorkflowAuthoringError("only an awaiting-review study may be completed")
        if outcome not in STUDY_OUTCOMES:
            raise WorkflowAuthoringError(f"invalid study outcome: {outcome}")
        reviewer = self._required_identity(reviewed_by, "reviewed-by")
        for filename in ("EVIDENCE.md", "CONCLUSION.md"):
            if not _is_substantive(path / filename):
                raise WorkflowAuthoringError(f"{filename} must be complete before completion")
        completion_path = path / "COMPLETION.json"
        if completion_path.exists():
            raise WorkflowAuthoringError("study already has completion evidence")

        occurred_at = timestamp_text(self.repository._current_time())
        completion: dict[str, Any] = {
            "schema_version": 1,
            "study_id": metadata.get("id"),
            "workflow": metadata.get("workflow"),
            "workflow_version": metadata.get("workflow_version"),
            "study_path": self._repo_relative(path),
            "outcome": outcome,
            "completed_at": occurred_at,
            "reviewed_by": reviewer,
            "preregistration_sha256": _sha256(path / "PREREGISTRATION.json"),
            "evidence_sha256": _sha256(path / "EVIDENCE.md"),
            "conclusion_sha256": _sha256(path / "CONCLUSION.md"),
        }
        metadata["status"] = "completed"
        metadata["outcome"] = outcome
        metadata["status_changed_at"] = occurred_at
        metadata["status_changed_by"] = reviewer
        metadata["status_reason"] = None
        metadata["completed_at"] = occurred_at
        metadata["reviewed_by"] = reviewer

        _atomic_write(completion_path, canonical_json_bytes(completion), replace=False)
        self._write_study_readme(path, metadata, document.body)
        self.repository.sync()
        self.repository._require_valid()
        return completion

    def _study_context(
        self,
        study_path: Path,
    ) -> tuple[Path, Path, dict[str, Any], MarkdownDocument]:
        path = self.repository._resolve_input(study_path)
        if not path.is_dir() or not STUDY_DIRECTORY_PATTERN.fullmatch(path.name):
            raise WorkflowAuthoringError(f"invalid study directory: {path}")
        version_path = self.repository._containing_version(path)
        if path.parent != (version_path / "work" / "studies").resolve():
            raise WorkflowAuthoringError(f"study is outside the version studies directory: {path}")
        _registry, workflow, version, record = self.repository._registered_version(version_path)
        document = read_markdown_document(path / "README.md")
        if (
            document.metadata.get("workflow") != workflow
            or document.metadata.get("workflow_version") != version
        ):
            raise WorkflowAuthoringError("study identity does not match its workflow version")
        return path, version_path, record, document

    def _normalize_revisits(self, revisits: str | None) -> str | None:
        if revisits is None:
            return None
        reference = revisits.strip()
        if not reference:
            raise WorkflowAuthoringError("revisits must identify an existing study")
        path = self.repository._resolve_repo_reference(reference)
        try:
            version_path = self.repository._containing_version(path)
        except WorkflowAuthoringError as exc:
            raise WorkflowAuthoringError("revisits must identify an existing study") from exc
        if (
            not path.is_dir()
            or not STUDY_DIRECTORY_PATTERN.fullmatch(path.name)
            or path.parent != (version_path / "work" / "studies").resolve()
        ):
            raise WorkflowAuthoringError("revisits must identify an existing study")
        return self._repo_relative(path)

    def _next_study_number(self, studies_root: Path) -> int:
        used: set[int] = set()
        for path in studies_root.iterdir():
            if not path.is_dir():
                continue
            match = STUDY_DIRECTORY_PATTERN.fullmatch(path.name)
            if match:
                used.add(int(match.group("number")))
        try:
            relative_root = studies_root.resolve().relative_to(self.repo_root.resolve())
            process = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_root.resolve()),
                    "log",
                    "--all",
                    "--format=",
                    "--name-only",
                    "--",
                    relative_root.as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired, ValueError):
            process = None
        if process is not None and process.returncode == 0:
            for line in process.stdout.splitlines():
                for component in Path(line).parts:
                    match = STUDY_DIRECTORY_PATTERN.fullmatch(component)
                    if match:
                        used.add(int(match.group("number")))
        return max(used, default=0) + 1

    def _repo_relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        except ValueError as exc:
            raise WorkflowAuthoringError(f"path is outside repository root: {path}") from exc

    @staticmethod
    def _required_identity(value: str, field: str) -> str:
        text = value.strip()
        if not text:
            raise WorkflowAuthoringError(f"{field} is required")
        return text

    @staticmethod
    def _write_study_readme(path: Path, metadata: dict[str, Any], body: str) -> None:
        _atomic_write(
            path / "README.md",
            render_markdown_document(MarkdownDocument(metadata, body)),
        )

    @staticmethod
    def _study_readme_body(title: str, workflow: str, version: str) -> str:
        return f"""# {title}

This study is pinned to `{workflow}@{version}`. Its lifecycle state is stored in this README
frontmatter; immutable preregistration and completion evidence are generated by the workflow CLI.

## Notes

Record only operational context here. Keep the frozen claim and method in `HYPOTHESIS.md` and
`PLAN.md`, execution references in `EVIDENCE.md`, and independent judgment in `CONCLUSION.md`.
"""

    @staticmethod
    def _hypothesis_template(title: str) -> str:
        return f"""# Hypothesis: {title}

## Claim

REPLACE_ME_STATE_A_FALSIFIABLE_CLAIM

## Decision relevance

REPLACE_ME_EXPLAIN_WHAT_DECISION_THE_RESULT_CHANGES

## Falsification conditions

REPLACE_ME_DEFINE_FAILURE_IN_ADVANCE
"""

    @staticmethod
    def _plan_template(title: str) -> str:
        return f"""# Plan: {title}

## Inputs and frozen identities

REPLACE_ME_LIST_EXACT_INPUTS_SNAPSHOTS_AND_DEPENDENCIES

## Method and stages

REPLACE_ME_MAP_THE_STUDY_TO_THE_PINNED_WORKFLOW_STAGES

## Metrics and outcome rules

REPLACE_ME_DEFINE_PASS_FAIL_INSUFFICIENT_AND_INDETERMINATE_RULES

## Deviations and stopping rules

REPLACE_ME_DEFINE_PROHIBITED_CHANGES_PAUSE_AND_TERMINATION_RULES
"""

    @staticmethod
    def _evidence_template(title: str) -> str:
        return f"""# Evidence: {title}

## Execution record

REPLACE_ME_RECORD_STAGE_RESULTS_AND_EXACT_IMMUTABLE_ARTIFACT_IDENTITIES

## Deviations and missing evidence

REPLACE_ME_RECORD_DEVIATIONS_WITHOUT_REWRITING_THE_FROZEN_PLAN
"""

    @staticmethod
    def _conclusion_template(title: str) -> str:
        return f"""# Conclusion: {title}

## Outcome

REPLACE_ME_SELECT_PASS_FAIL_INSUFFICIENT_EVIDENCE_OR_INDETERMINATE

## Evidence trace

REPLACE_ME_CONNECT_EACH_JUDGMENT_TO_EXACT_EVIDENCE

## Limitations and follow-up

REPLACE_ME_RECORD_UNCERTAINTY_WITHOUT_REPAIRING_THE_STUDY_RETROACTIVELY
"""

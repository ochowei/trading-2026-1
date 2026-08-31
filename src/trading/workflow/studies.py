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
from trading.core.ledger_storage import locked_file
from trading.core.qualification_transaction import qualification_transaction_journal_path
from trading.workflow.authoring import (
    SLUG_PATTERN,
    STUDY_DIRECTORY_PATTERN,
    STUDY_OUTCOMES,
    STUDY_ROUTES,
    MarkdownDocument,
    WorkflowAuthoringError,
    WorkflowRepository,
    _atomic_write,
    _is_substantive,
    _sha256,
    read_markdown_document,
    render_markdown_document,
)
from trading.workflow.study_qualification import (
    CANDIDATE_FREEZE_AUTHORIZATION_SCOPE,
    REQUIRED_STUDY_TIME_CHALLENGES,
    STUDY_QUALIFICATION_CAPABILITY,
    frozen_study_qualification_registry_path,
    qualification_study_registration_lock_path,
    structured_qualification_runtime_contract,
    validate_candidate_freeze_for_study,
    validate_study_qualification_spec_for_preregistration,
)
from trading.workflow.terminal_evidence import validate_study_time_terminal_evidence

_STUDY_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"cancelled"}),
    "preregistered": frozenset({"running", "cancelled"}),
    "running": frozenset({"paused", "awaiting-review", "cancelled"}),
    "paused": frozenset({"running", "cancelled"}),
    "awaiting-review": frozenset({"running"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
}

DEVELOPMENT_AUTHORIZATION_FILENAME = "DEVELOPMENT_AUTHORIZATION.json"
CANDIDATE_FREEZE_FILENAME = "CANDIDATE_FREEZE.json"


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
        route: str | None = None,
    ) -> Path:
        """Create the next local study draft under an active workflow version."""
        self.repository._require_structurally_valid()
        version_resolved = self.repository._resolve_input(version_path)
        _registry, workflow, version, _record = self.repository._registered_version(
            version_resolved
        )
        self._require_study_authority(
            version_resolved,
            _record,
            inactive_message="new studies require an active workflow version",
        )
        if not SLUG_PATTERN.fullmatch(study_slug):
            raise WorkflowAuthoringError("study slug must be lowercase kebab-case")
        title_text = self._required_identity(title, "study title")
        creator = self._required_identity(created_by, "created-by")
        revisits_path = self._normalize_revisits(revisits)
        release = self._release_payload(version_resolved)
        structured_routes = STUDY_QUALIFICATION_CAPABILITY in release.get("capabilities", [])
        if structured_routes and route is None:
            raise WorkflowAuthoringError("released workflow requires an explicit study route")
        if route is not None and route not in STUDY_ROUTES:
            raise WorkflowAuthoringError(f"invalid study route: {route}")
        if route == "study-time-retrospective":
            if STUDY_QUALIFICATION_CAPABILITY not in release.get("capabilities", []):
                raise WorkflowAuthoringError(
                    "released workflow does not authorize the study-time-retrospective route"
                )

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
            "route": route,
            "disposition": None,
            "decision_stage": None,
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
        if structured_routes:
            files["QUALIFICATION_SPEC.json"] = canonical_json_bytes(
                self._qualification_spec_template(target, str(route))
            )
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
        path, version_path, _version_record, document = self._study_context(study_path)
        metadata = copy.deepcopy(document.metadata)
        if metadata.get("status") != "draft":
            raise WorkflowAuthoringError("only a draft study may be preregistered")
        self._require_study_authority(
            version_path,
            _version_record,
            inactive_message="only an active workflow version may preregister a study",
        )
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

        qualification_spec_sha256 = None
        structured_routes = STUDY_QUALIFICATION_CAPABILITY in release.get("capabilities", [])
        if structured_routes and metadata.get("route") is None:
            raise WorkflowAuthoringError("released workflow requires an explicit study route")
        if structured_routes:
            if metadata.get("route") not in STUDY_ROUTES:
                raise WorkflowAuthoringError("released workflow requires a valid study route")
            if metadata.get("route") == "study-time-retrospective" and (
                STUDY_QUALIFICATION_CAPABILITY not in release.get("capabilities", [])
            ):
                raise WorkflowAuthoringError(
                    "released workflow lacks study-time-retrospective capability"
                )
            try:
                qualification_spec_sha256 = validate_study_qualification_spec_for_preregistration(
                    path
                )
            except ValueError as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
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
        if metadata.get("route") is not None:
            registration["route"] = metadata.get("route")
        if qualification_spec_sha256 is not None:
            registration["qualification_spec_sha256"] = qualification_spec_sha256
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

    @staticmethod
    def _release_payload(version_path: Path) -> dict[str, Any]:
        try:
            payload = json.loads((version_path / "RELEASE.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkflowAuthoringError(f"cannot read workflow release: {exc}") from exc
        if not isinstance(payload, dict):
            raise WorkflowAuthoringError("workflow release must be an object")
        return payload

    def _require_study_authority(
        self,
        version_path: Path,
        version_record: dict[str, Any],
        *,
        inactive_message: str,
    ) -> None:
        if version_record.get("status") != "active":
            raise WorkflowAuthoringError(inactive_message)
        try:
            self.repository.require_effective_version(version_path)
        except WorkflowAuthoringError as exc:
            message = str(exc)
            if "is not registered" in message or "cannot read" in message:
                # Unit-level seams may supply a synthetic active context after structural
                # validation has been replaced. Real operations always have a valid registry.
                return
            raise

    def transition(
        self,
        study_path: Path,
        target_status: str,
        *,
        actor: str,
        reason: str | None = None,
        approved_by: str | None = None,
    ) -> None:
        """Apply one legal non-completion study transition."""
        self.repository._require_structurally_valid()
        path, version_path, _version_record, document = self._study_context(study_path)
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
        administrative_review_return = current == "awaiting-review" and target_status == "running"
        if target_status == "running" and not administrative_review_return:
            self._require_study_authority(
                version_path,
                _version_record,
                inactive_message="only an active workflow version may start or resume work",
            )
        if target_status == "awaiting-review" and not _is_substantive(path / "EVIDENCE.md"):
            raise WorkflowAuthoringError("EVIDENCE.md must be complete before review")

        occurred_at = timestamp_text(self.repository._current_time())
        release = self._release_payload(version_path)
        structured_routes = STUDY_QUALIFICATION_CAPABILITY in release.get("capabilities", [])
        if structured_routes and current == "preregistered" and target_status == "running":
            approver = self._required_identity(approved_by, "approved-by")
            if approver != metadata.get("preregistered_by"):
                raise WorkflowAuthoringError(
                    "Development approval must come from the preregistered human owner"
                )
            authorization_path = path / DEVELOPMENT_AUTHORIZATION_FILENAME
            authorization = {
                "schema_version": 1,
                "study_path": self._repo_relative(path),
                "route": metadata.get("route"),
                "preregistration_sha256": _sha256(path / "PREREGISTRATION.json"),
                "authorized_at": occurred_at,
                "approved_by": approver,
                "authorized_operator": actor_text,
                "authorization_scope": (
                    "Begin outcome-relevant Development under the exact preregistered "
                    "route only; no Evaluation, Shadow, broker, or order authority."
                ),
            }
            if authorization_path.exists():
                try:
                    existing = json.loads(authorization_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise WorkflowAuthoringError(
                        f"cannot recover Development authorization: {exc}"
                    ) from exc
                comparable = dict(authorization)
                comparable.pop("authorized_at")
                if not isinstance(existing, dict) or any(
                    existing.get(field) != value for field, value in comparable.items()
                ):
                    raise WorkflowAuthoringError(
                        "existing Development authorization belongs to a different operation"
                    )
                recovered_at = existing.get("authorized_at")
                if not isinstance(recovered_at, str) or not recovered_at:
                    raise WorkflowAuthoringError(
                        "existing Development authorization time is invalid"
                    )
                occurred_at = recovered_at
            else:
                _atomic_write(
                    authorization_path,
                    canonical_json_bytes(authorization),
                    replace=False,
                )
        elif approved_by is not None:
            raise WorkflowAuthoringError(
                "--approved-by is used only for first Development authorization"
            )

        metadata["status"] = target_status
        metadata["status_changed_at"] = occurred_at
        metadata["status_changed_by"] = actor_text
        metadata["status_reason"] = reason_text
        self._write_study_readme(path, metadata, document.body)
        self.repository.sync()
        self.repository._require_valid()

    def _qualification_spec_template(self, study_path: Path, route: str) -> dict[str, Any]:
        """Return the incomplete structured template every capability-scoped route must freeze."""
        classification = "verified-clean" if route == "clean-historical" else "provenance-unknown"
        try:
            runtime_contract = structured_qualification_runtime_contract(study_path.parents[2])
        except ValueError as exc:
            raise WorkflowAuthoringError(
                f"cannot freeze released policy/runtime contract: {exc}"
            ) from exc
        return {
            "schema_version": 1,
            "study_path": self._repo_relative(study_path),
            "route": route,
            "evidence_classification": classification,
            "evidence_justification": "",
            "trial_history_complete": False,
            "prior_selection_history_incomplete": True,
            "registries": {
                "trial_registry_path": "results/registries/trial_registry.json",
                "qualification_registry_path": "state/qualification-registry.json",
            },
            **runtime_contract,
            "calendar": {
                "warmup_start": None,
                "warmup_end": None,
                "development_years": [],
                "quarantine_years": [],
                "evaluation_years": [],
            },
            "family": {
                "maximum_trials": 0,
                "baseline_identity": None,
                "members": [],
                "shared_sources": [],
            },
            "execution": {},
            "benchmarks": {},
            "required_challenges": [
                {
                    "id": challenge,
                    "evidence_identity": f"{challenge}-evidence",
                    "applies_to": {
                        "kind": (
                            "benchmark"
                            if challenge in {"cash", "random-entry"}
                            else "trial"
                            if challenge == "family-baseline"
                            else "method"
                        ),
                        "identities": [
                            challenge
                            if challenge in {"cash", "random-entry"}
                            else "REPLACE-family-baseline-identity"
                            if challenge == "family-baseline"
                            else f"REPLACE-{challenge}-identity"
                        ],
                    },
                    "gate": {},
                }
                for challenge in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
            ],
        }

    def freeze_candidate(
        self,
        study_path: Path,
        *,
        selection_path: Path,
        approved_by: str,
    ) -> dict[str, Any]:
        """Add the current-time human-approved candidate/family freeze exactly once."""
        self.repository._require_structurally_valid()
        path, version_path, _version_record, document = self._study_context(study_path)
        metadata = document.metadata
        if metadata.get("status") != "running":
            raise WorkflowAuthoringError("candidate freeze requires a running Development study")
        self._require_study_authority(
            version_path,
            _version_record,
            inactive_message="candidate freeze requires an active workflow version",
        )
        release = self._release_payload(version_path)
        if STUDY_QUALIFICATION_CAPABILITY not in release.get("capabilities", []):
            raise WorkflowAuthoringError(
                "released workflow does not authorize guarded candidate freezes"
            )
        approver = self._required_identity(approved_by, "approved-by")
        if approver != metadata.get("preregistered_by"):
            raise WorkflowAuthoringError(
                "candidate freeze approval must come from the preregistered human owner"
            )
        try:
            selection = json.loads(Path(selection_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkflowAuthoringError(f"cannot read Development selection: {exc}") from exc
        if not isinstance(selection, dict) or set(selection) != {
            "selected_candidate",
            "family_baseline",
            "complete_family",
        }:
            raise WorkflowAuthoringError(
                "Development selection must contain only selected_candidate, family_baseline, "
                "and complete_family"
            )
        try:
            preregistration = json.loads(
                (path / "PREREGISTRATION.json").read_text(encoding="utf-8")
            )
            spec = json.loads((path / "QUALIFICATION_SPEC.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkflowAuthoringError(f"cannot read frozen study identity: {exc}") from exc
        if not isinstance(preregistration, dict) or not isinstance(spec, dict):
            raise WorkflowAuthoringError("frozen study identity is malformed")
        family = spec.get("family")
        if not isinstance(family, dict):
            raise WorkflowAuthoringError("qualification spec family is malformed")

        freeze_path = path / CANDIDATE_FREEZE_FILENAME
        if freeze_path.exists():
            try:
                existing = json.loads(freeze_path.read_text(encoding="utf-8"))
                if not isinstance(existing, dict):
                    raise ValueError("candidate freeze must be an object")
                validate_candidate_freeze_for_study(path, existing)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                raise WorkflowAuthoringError(f"cannot recover candidate freeze: {exc}") from exc
            if existing.get("approved_by") != approver or any(
                existing.get(field) != selection[field] for field in selection
            ):
                raise WorkflowAuthoringError(
                    "existing candidate freeze belongs to a different operation"
                )
            return existing

        freeze = {
            "schema_version": 1,
            "study_id": preregistration.get("study_id"),
            "study_path": preregistration.get("study_path"),
            "workflow": preregistration.get("workflow"),
            "workflow_version": preregistration.get("workflow_version"),
            "route": preregistration.get("route"),
            "approved_at": timestamp_text(self.repository._current_time()),
            "approved_by": approver,
            "authorization_scope": CANDIDATE_FREEZE_AUTHORIZATION_SCOPE,
            "hypothesis_sha256": _sha256(path / "HYPOTHESIS.md"),
            "plan_sha256": _sha256(path / "PLAN.md"),
            "qualification_spec_sha256": _sha256(path / "QUALIFICATION_SPEC.json"),
            "preregistration_sha256": _sha256(path / "PREREGISTRATION.json"),
            "development_authorization_sha256": _sha256(path / DEVELOPMENT_AUTHORIZATION_FILENAME),
            "workflow_release_sha256": _sha256(version_path / "RELEASE.json"),
            "frozen_trial_budget": family.get("maximum_trials"),
            **selection,
        }
        try:
            validate_candidate_freeze_for_study(path, freeze)
        except ValueError as exc:
            raise WorkflowAuthoringError(str(exc)) from exc
        try:
            _atomic_write(freeze_path, canonical_json_bytes(freeze), replace=False)
        except WorkflowAuthoringError as exc:
            if not freeze_path.exists():
                raise
            try:
                existing = json.loads(freeze_path.read_text(encoding="utf-8"))
                if not isinstance(existing, dict):
                    raise ValueError("candidate freeze must be an object")
                validate_candidate_freeze_for_study(path, existing)
            except (OSError, json.JSONDecodeError, ValueError) as recovery_exc:
                raise WorkflowAuthoringError(
                    f"cannot recover concurrent candidate freeze: {recovery_exc}"
                ) from recovery_exc
            if existing.get("approved_by") != approver or any(
                existing.get(field) != selection[field] for field in selection
            ):
                raise WorkflowAuthoringError(
                    "existing candidate freeze belongs to a different operation"
                ) from exc
            return existing
        self.repository.sync()
        self.repository._require_valid()
        return freeze

    def complete(
        self,
        study_path: Path,
        *,
        outcome: str,
        reviewed_by: str,
        disposition: str | None = None,
        decision_stage: str | None = None,
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
        self._validate_terminal_decision(
            route=metadata.get("route"),
            outcome=outcome,
            disposition=disposition,
            decision_stage=decision_stage,
        )
        if metadata.get("route") == "study-time-retrospective":
            try:
                registry_path = frozen_study_qualification_registry_path(path)
            except ValueError as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
            with locked_file(qualification_study_registration_lock_path(registry_path), 10.0):
                if qualification_transaction_journal_path(registry_path).exists():
                    raise WorkflowAuthoringError(
                        "study completion cannot bypass a pending qualification transaction"
                    )
                return self._complete_locked(
                    path=path,
                    metadata=metadata,
                    document=document,
                    outcome=outcome,
                    reviewer=reviewer,
                    disposition=disposition,
                    decision_stage=decision_stage,
                    require_current_registry=(
                        outcome == "fail" and decision_stage == "development"
                    ),
                )
        return self._complete_locked(
            path=path,
            metadata=metadata,
            document=document,
            outcome=outcome,
            reviewer=reviewer,
            disposition=disposition,
            decision_stage=decision_stage,
            require_current_registry=False,
        )

    def _complete_locked(
        self,
        *,
        path: Path,
        metadata: dict[str, Any],
        document: MarkdownDocument,
        outcome: str,
        reviewer: str,
        disposition: str | None,
        decision_stage: str | None,
        require_current_registry: bool,
    ) -> dict[str, Any]:
        """Complete after any stage-specific serialization lock has been acquired."""
        terminal_evidence_sha256 = None
        if metadata.get("route") == "study-time-retrospective":
            if decision_stage is None:
                raise WorkflowAuthoringError("study-time terminal decision needs a stage")
            try:
                terminal_evidence_sha256 = validate_study_time_terminal_evidence(
                    study_path=path,
                    outcome=outcome,
                    disposition=disposition,
                    decision_stage=decision_stage,
                    require_current_registry=require_current_registry,
                )
            except ValueError as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
            replay_issues: list[Any] = []
            self.repository._validate_study_time_terminal(
                {
                    "outcome": outcome,
                    "disposition": disposition,
                    "decision_stage": decision_stage,
                },
                path / "README.md",
                replay_issues,
            )
            if replay_issues:
                raise WorkflowAuthoringError(
                    "terminal evidence is not tracked/replayable before completion: "
                    + "; ".join(issue.message for issue in replay_issues)
                )
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
        for field, value in (
            ("route", metadata.get("route")),
            ("disposition", disposition),
            ("decision_stage", decision_stage),
        ):
            if value is not None:
                completion[field] = value
        if terminal_evidence_sha256 is not None:
            completion["terminal_evidence_sha256"] = terminal_evidence_sha256
        metadata["status"] = "completed"
        metadata["outcome"] = outcome
        metadata["status_changed_at"] = occurred_at
        metadata["status_changed_by"] = reviewer
        metadata["status_reason"] = None
        metadata["completed_at"] = occurred_at
        metadata["reviewed_by"] = reviewer
        metadata["disposition"] = disposition
        metadata["decision_stage"] = decision_stage

        _atomic_write(completion_path, canonical_json_bytes(completion), replace=False)
        self._write_study_readme(path, metadata, document.body)
        self.repository.sync()
        self.repository._require_valid()
        return completion

    @staticmethod
    def _validate_terminal_decision(
        *,
        route: object,
        outcome: str,
        disposition: str | None,
        decision_stage: str | None,
    ) -> None:
        if route != "study-time-retrospective":
            if disposition is not None or decision_stage is not None:
                raise WorkflowAuthoringError(
                    "terminal disposition fields require a study-time-retrospective route"
                )
            return
        valid = False
        if outcome == "pass":
            valid = (
                disposition == "retrospectively-supported"
                and decision_stage == "retrospective-evaluation"
            )
        elif outcome == "fail":
            valid = (disposition, decision_stage) in {
                ("development-selection-failed", "development"),
                ("retrospective-screen-failed", "retrospective-evaluation"),
            }
        elif outcome == "indeterminate":
            valid = disposition is None and decision_stage in {
                "development",
                "candidate-freeze",
                "retrospective-evaluation",
                "independent-review",
            }
        if not valid:
            raise WorkflowAuthoringError(
                "study-time retrospective outcome, disposition, and decision stage conflict"
            )

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
    def _required_identity(value: str | None, field: str) -> str:
        text = str(value or "").strip()
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

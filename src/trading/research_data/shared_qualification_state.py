"""Git-common private authority for worktree-independent qualification state."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from trading.core.accounting import canonical_json_bytes, timestamp_text
from trading.core.ledger_storage import atomic_write, locked_file
from trading.core.qualification import QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY
from trading.research_data.qualification_registry import QualificationRegistry
from trading.workflow.authoring import (
    WorkflowAuthoringError,
    WorkflowRepository,
    _sha256,
    read_markdown_document,
)

SHARED_QUALIFICATION_STATE_CAPABILITY = "shared-qualification-state-v1"
CROSS_CHAIN_PLAN_ADMINISTRATION_CAPABILITY = "cross-chain-plan-administration-v1"
SHARED_QUALIFICATION_STATE_SCHEMA_VERSION = 1
DEFAULT_LOGICAL_REGISTRY_IDENTITY = "state/qualification-registry.json"
_GENESIS_HASH = "0" * 64


class SharedQualificationStateError(RuntimeError):
    """Shared qualification state is incomplete, conflicting, or unauthorized."""


@dataclass(frozen=True, slots=True)
class GitRepositoryIdentity:
    """Verified repository/worktree identity used to locate private shared state."""

    repository_root: Path
    common_git_directory: Path
    repository_id: str
    worktree_roots: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class SharedQualificationPaths:
    """All mutable paths derived from one verified repository identity."""

    root: Path
    catalog: Path
    active_registry: Path
    migration_lock: Path
    transaction_journal: Path

    @property
    def active_checkpoint(self) -> Path:
        return self.active_registry.with_name(f".{self.active_registry.name}.head.json")

    @property
    def study_registration_lock(self) -> Path:
        return self.active_registry.with_name(
            f".{self.active_registry.name}.study-registration.lock"
        )


@dataclass(frozen=True, slots=True)
class MigrationSource:
    """One explicit legacy registry/checkpoint pair."""

    registry_path: Path
    checkpoint_path: Path


@dataclass(frozen=True, slots=True)
class SharedMigrationRequest:
    """Closed human-authored inputs for a complete shared-state migration."""

    logical_registry_identity: str
    approved_by: str
    sources: tuple[MigrationSource, ...]

    @classmethod
    def from_path(cls, path: Path) -> SharedMigrationRequest:
        try:
            payload = json.loads(Path(path).read_bytes())
        except (OSError, json.JSONDecodeError) as exc:
            raise SharedQualificationStateError(f"cannot read migration request: {exc}") from exc
        if not isinstance(payload, dict) or set(payload) != {
            "schema_version",
            "logical_registry_identity",
            "approved_by",
            "sources",
        }:
            raise SharedQualificationStateError("migration request fields are invalid")
        if payload.get("schema_version") != 1:
            raise SharedQualificationStateError("migration request schema_version must be 1")
        logical_identity = _safe_relative_identity(
            payload.get("logical_registry_identity"), "logical registry identity"
        )
        approved_by = _required_text(payload.get("approved_by"), "migration approver")
        raw_sources = payload.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise SharedQualificationStateError("migration request requires source pairs")
        sources: list[MigrationSource] = []
        for raw_source in raw_sources:
            if not isinstance(raw_source, dict) or set(raw_source) != {
                "registry_path",
                "checkpoint_path",
            }:
                raise SharedQualificationStateError("migration source fields are invalid")
            registry = _absolute_path(raw_source.get("registry_path"), "source registry")
            checkpoint = _absolute_path(raw_source.get("checkpoint_path"), "source checkpoint")
            expected_checkpoint = registry.with_name(f".{registry.name}.head.json")
            if checkpoint != expected_checkpoint:
                raise SharedQualificationStateError(
                    "source checkpoint is not the canonical sidecar for its registry"
                )
            sources.append(MigrationSource(registry, checkpoint))
        registry_paths = [source.registry_path for source in sources]
        if len(registry_paths) != len(set(registry_paths)):
            raise SharedQualificationStateError("migration source registries must be unique")
        return cls(logical_identity, approved_by, tuple(sources))


@dataclass(frozen=True, slots=True)
class MigrationPreview:
    """Derived, replay-verified migration decision awaiting exact approval."""

    catalog: dict[str, object]
    decision_sha256: str
    open_plans_by_family: dict[str, tuple[str, ...]]
    shared_paths: SharedQualificationPaths

    def as_payload(self) -> dict[str, object]:
        return {
            "schema_version": SHARED_QUALIFICATION_STATE_SCHEMA_VERSION,
            "decision_sha256": self.decision_sha256,
            "shared_root": str(self.shared_paths.root),
            "repository_id": self.catalog["repository_id"],
            "source_count": len(self.catalog["shards"]),
            "open_plans_by_family": {
                family: list(plan_ids)
                for family, plan_ids in sorted(self.open_plans_by_family.items())
            },
            "catalog": self.catalog,
        }


def resolve_git_repository_identity(repository_root: Path) -> GitRepositoryIdentity:
    """Resolve one common Git directory and every currently registered worktree."""
    requested = Path(repository_root).resolve()
    top_level = Path(_git_output(requested, "rev-parse", "--show-toplevel")).resolve()
    if requested != top_level:
        raise SharedQualificationStateError(
            "repository root must be the exact verified Git worktree top-level"
        )
    common_text = _git_output(requested, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common = Path(common_text).resolve()
    if not common.is_dir():
        raise SharedQualificationStateError("verified Git common directory does not exist")
    porcelain = _git_output(requested, "worktree", "list", "--porcelain")
    roots = tuple(
        sorted(
            {
                Path(line.removeprefix("worktree ")).resolve()
                for line in porcelain.splitlines()
                if line.startswith("worktree ")
            },
            key=str,
        )
    )
    if requested not in roots:
        raise SharedQualificationStateError(
            "current repository is absent from Git worktree inventory"
        )
    repository_id = hashlib.sha256(str(common).encode()).hexdigest()
    return GitRepositoryIdentity(requested, common, repository_id, roots)


def shared_qualification_paths(identity: GitRepositoryIdentity) -> SharedQualificationPaths:
    """Derive all shared paths without consulting a caller-selected state path."""
    root = (
        identity.common_git_directory
        / "trading-private-state"
        / identity.repository_id
        / "qualification"
    )
    active = root / "active" / "qualification-registry.json"
    return SharedQualificationPaths(
        root=root,
        catalog=root / "catalog.json",
        active_registry=active,
        migration_lock=root.parent / ".qualification-migration.lock",
        transaction_journal=root.parent / ".qualification-migration-transaction.json",
    )


def resolve_workflow_qualification_registry_path(
    repository_root: Path,
    workflow_path: Path,
    *,
    logical_identity: str = DEFAULT_LOGICAL_REGISTRY_IDENTITY,
    require_effective_shared: bool = True,
) -> Path:
    """Map one workflow's logical registry identity to its operational authority."""
    root = Path(repository_root).resolve()
    logical = _safe_relative_identity(logical_identity, "logical registry identity")
    workflow = Path(workflow_path).resolve()
    release_path = workflow / "RELEASE.json"
    if not release_path.is_file():
        readme_path = workflow / "README.md"
        capabilities = (
            read_markdown_document(readme_path).metadata.get("capabilities", [])
            if readme_path.is_file()
            else []
        )
        if isinstance(capabilities, list) and SHARED_QUALIFICATION_STATE_CAPABILITY in capabilities:
            raise SharedQualificationStateError(
                "shared-capability workflow release is required for registry resolution"
            )
        return (root / logical).resolve()
    try:
        release = json.loads(release_path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise SharedQualificationStateError(f"cannot read workflow release: {exc}") from exc
    capabilities = release.get("capabilities", []) if isinstance(release, Mapping) else None
    if not isinstance(capabilities, list):
        raise SharedQualificationStateError("workflow release capabilities are malformed")
    if SHARED_QUALIFICATION_STATE_CAPABILITY not in capabilities:
        return (root / logical).resolve()
    if require_effective_shared:
        _require_effective_capabilities(
            workflow,
            {SHARED_QUALIFICATION_STATE_CAPABILITY},
        )
    shared = SharedQualificationState(root)
    shared.global_projection()
    return shared.paths.active_registry


def resolve_study_qualification_registry_path(
    study_path: Path,
    *,
    logical_identity: str = DEFAULT_LOGICAL_REGISTRY_IDENTITY,
) -> Path:
    """Resolve a frozen study without converting its logical evidence identity."""
    study = Path(study_path).resolve()
    try:
        repository_root = study.parents[4]
        workflow_path = study.parents[2]
    except IndexError as exc:
        raise SharedQualificationStateError("study path is outside the workflow layout") from exc
    return resolve_workflow_qualification_registry_path(
        repository_root,
        workflow_path,
        logical_identity=logical_identity,
        require_effective_shared=False,
    )


class SharedQualificationState:
    """Preview, publish, and replay one repository's shared qualification authority."""

    def __init__(self, repository_root: Path, *, lock_timeout_seconds: float = 10.0) -> None:
        self.identity = resolve_git_repository_identity(repository_root)
        self.paths = shared_qualification_paths(self.identity)
        self.lock_timeout_seconds = lock_timeout_seconds

    def preview_migration(
        self,
        request: SharedMigrationRequest,
        *,
        workflow_path: Path,
        allow_pending_journal: bool = False,
    ) -> MigrationPreview:
        """Produce a read-only exact migration decision for human approval."""
        _require_declared_capability(
            workflow_path,
            SHARED_QUALIFICATION_STATE_CAPABILITY,
            require_effective=False,
        )
        discovered = self._discover_source_registries(request.logical_registry_identity)
        requested = {source.registry_path for source in request.sources}
        if requested != discovered:
            missing = sorted(str(path) for path in discovered - requested)
            extra = sorted(str(path) for path in requested - discovered)
            details = []
            if missing:
                details.append("missing=" + ",".join(missing))
            if extra:
                details.append("unregistered=" + ",".join(extra))
            raise SharedQualificationStateError(
                "migration inventory is not complete"
                + (": " + "; ".join(details) if details else "")
            )
        if self.paths.transaction_journal.exists() and not allow_pending_journal:
            raise SharedQualificationStateError("shared migration transaction journal is pending")

        shards: list[dict[str, object]] = []
        seen_event_ids: dict[str, Path] = {}
        open_plans: dict[str, list[str]] = {}
        for source in sorted(request.sources, key=lambda item: str(item.registry_path)):
            self._validate_source_is_quiescent(source.registry_path)
            registry_bytes = source.registry_path.read_bytes()
            checkpoint_bytes = source.checkpoint_path.read_bytes()
            state = _replay_registry_pair(registry_bytes, checkpoint_bytes)
            registry_digest = hashlib.sha256(registry_bytes).hexdigest()
            checkpoint_digest = hashlib.sha256(checkpoint_bytes).hexdigest()
            events = _events(state)
            for event in events:
                event_id = _required_text(event.get("event_id"), "qualification event identity")
                if event_id in seen_event_ids:
                    raise SharedQualificationStateError(
                        f"event identity collision across source registries: {event_id}"
                    )
                seen_event_ids[event_id] = source.registry_path
            terminals = {
                payload.get("plan_id")
                for event in events
                if event.get("event_type")
                in {
                    "historical_screen",
                    "historical_plan_abandoned",
                    "historical_plan_closed_invalidated",
                }
                and isinstance((payload := event.get("payload")), Mapping)
            }
            plans: list[dict[str, object]] = []
            for event in events:
                if event.get("event_type") != "historical_plan":
                    continue
                payload = _mapping(event.get("payload"), "historical plan payload")
                plan_id = _required_text(payload.get("plan_id"), "historical plan identity")
                family = _required_text(payload.get("experiment_family"), "experiment family")
                plans.append(
                    {
                        "plan_id": plan_id,
                        "experiment_family": family,
                        "event_hash": _required_sha256(
                            event.get("event_hash"), "historical plan event hash"
                        ),
                        "study_identity": payload.get("study_identity"),
                        "open": plan_id not in terminals,
                    }
                )
                if plan_id not in terminals:
                    open_plans.setdefault(family, []).append(plan_id)
            head = _mapping(json.loads(checkpoint_bytes), "source checkpoint")
            shards.append(
                {
                    "registry_sha256": registry_digest,
                    "checkpoint_sha256": checkpoint_digest,
                    "event_count": len(events),
                    "head_hash": _required_sha256(head.get("head_hash"), "source head hash"),
                    "source_registry_path": str(source.registry_path),
                    "source_checkpoint_path": str(source.checkpoint_path),
                    "plans": plans,
                }
            )
        if len({shard["registry_sha256"] for shard in shards}) != len(shards):
            raise SharedQualificationStateError(
                "duplicate registry bytes require one unambiguous source attestation"
            )
        catalog: dict[str, object] = {
            "schema_version": SHARED_QUALIFICATION_STATE_SCHEMA_VERSION,
            "repository_id": self.identity.repository_id,
            "common_git_directory_sha256": hashlib.sha256(
                str(self.identity.common_git_directory).encode()
            ).hexdigest(),
            "logical_registry_identity": request.logical_registry_identity,
            "generation": 1,
            "approved_by": request.approved_by,
            "shards": shards,
            "active_chain": {
                "identity": "active/qualification-registry.json",
                "event_count": 0,
                "head_hash": _GENESIS_HASH,
            },
        }
        decision = {
            "schema_version": 1,
            "operation": "shared-qualification-state-initial-migration",
            "catalog": catalog,
        }
        decision_sha256 = hashlib.sha256(canonical_json_bytes(decision)).hexdigest()
        return MigrationPreview(
            catalog=catalog,
            decision_sha256=decision_sha256,
            open_plans_by_family={
                family: tuple(sorted(plan_ids)) for family, plan_ids in open_plans.items()
            },
            shared_paths=self.paths,
        )

    def apply_migration(
        self,
        request: SharedMigrationRequest,
        *,
        workflow_path: Path,
        approved_decision_sha256: str,
    ) -> MigrationPreview:
        """Publish one exact approved migration, or recover that exact decision."""
        _require_effective_capabilities(
            workflow_path,
            {SHARED_QUALIFICATION_STATE_CAPABILITY},
        )
        approved_digest = _required_sha256(approved_decision_sha256, "approved migration decision")
        with locked_file(self.paths.migration_lock, self.lock_timeout_seconds):
            preview = self.preview_migration(
                request,
                workflow_path=workflow_path,
                allow_pending_journal=True,
            )
            if preview.decision_sha256 != approved_digest:
                raise SharedQualificationStateError(
                    "approved migration decision does not match current inventory bytes"
                )
            journal = {
                "schema_version": 1,
                "decision_sha256": preview.decision_sha256,
                "repository_id": self.identity.repository_id,
                "approved_by": request.approved_by,
                "catalog_sha256": hashlib.sha256(canonical_json_bytes(preview.catalog)).hexdigest(),
            }
            if self.paths.transaction_journal.exists():
                try:
                    existing_journal = json.loads(self.paths.transaction_journal.read_bytes())
                except (OSError, json.JSONDecodeError) as exc:
                    raise SharedQualificationStateError(
                        f"cannot recover shared migration journal: {exc}"
                    ) from exc
                if existing_journal != journal:
                    raise SharedQualificationStateError(
                        "pending shared migration journal belongs to a different decision"
                    )
            else:
                self.paths.root.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                atomic_write(
                    self.paths.transaction_journal,
                    canonical_json_bytes(journal),
                    replace=False,
                )
            if self.paths.root.exists():
                self._verify_existing_decision(preview)
                self.paths.transaction_journal.unlink(missing_ok=True)
                return preview
            stage = Path(
                tempfile.mkdtemp(prefix=".qualification-stage-", dir=self.paths.root.parent)
            )
            try:
                for source, shard in zip(
                    sorted(request.sources, key=lambda item: str(item.registry_path)),
                    preview.catalog["shards"],
                    strict=True,
                ):
                    digest = str(_mapping(shard, "catalog shard")["registry_sha256"])
                    shard_root = stage / "shards" / digest
                    shard_root.mkdir(parents=True, exist_ok=False, mode=0o700)
                    _write_exact(
                        shard_root / "qualification-registry.json",
                        source.registry_path,
                        expected_sha256=digest,
                    )
                    _write_exact(
                        shard_root / ".qualification-registry.json.head.json",
                        source.checkpoint_path,
                        expected_sha256=str(_mapping(shard, "catalog shard")["checkpoint_sha256"]),
                    )
                active = QualificationRegistry(stage / "active" / "qualification-registry.json")
                active.initialize()
                atomic_write(
                    stage / "catalog.json",
                    canonical_json_bytes(preview.catalog),
                    replace=False,
                )
                os.replace(stage, self.paths.root)
                stage = Path()
                self._verify_existing_decision(preview)
                self.paths.transaction_journal.unlink()
            finally:
                if stage != Path() and stage.exists():
                    shutil.rmtree(stage)
            return preview

    def global_projection(self) -> dict[str, object]:
        """Replay every catalog shard and the active chain into one lifecycle view."""
        catalog = self._load_catalog()
        plan_sources: dict[str, dict[str, object]] = {}
        terminals: dict[str, dict[str, object]] = {}
        for chain, source in self._registered_chains(catalog):
            state = QualificationRegistry(chain).read()
            for event in _events(state):
                payload = _mapping(event.get("payload"), "qualification event payload")
                event_type = event.get("event_type")
                if event_type == "historical_plan":
                    plan_id = _required_text(payload.get("plan_id"), "historical plan identity")
                    if plan_id in plan_sources:
                        raise SharedQualificationStateError(
                            f"duplicate historical plan across shared chains: {plan_id}"
                        )
                    plan_sources[plan_id] = {
                        "plan": payload,
                        "plan_event_hash": event.get("event_hash"),
                        **source,
                    }
                elif event_type in {
                    "historical_screen",
                    "historical_plan_abandoned",
                    "historical_plan_closed_invalidated",
                }:
                    plan_id = _required_text(payload.get("plan_id"), "terminal plan identity")
                    if plan_id in terminals:
                        raise SharedQualificationStateError(
                            f"duplicate terminal facts across shared chains: {plan_id}"
                        )
                    terminals[plan_id] = {"event": event, **source}
        for plan_id, terminal in terminals.items():
            plan_source = plan_sources.get(plan_id)
            if plan_source is None:
                raise SharedQualificationStateError(
                    f"terminal fact precedes its source plan: {plan_id}"
                )
            event = _mapping(terminal["event"], "terminal event")
            payload = _mapping(event.get("payload"), "terminal payload")
            binding = payload.get("source_binding")
            if binding is not None:
                binding = _mapping(binding, "terminal source binding")
                expected = {
                    "registry_sha256": plan_source["registry_sha256"],
                    "head_hash": plan_source["head_hash"],
                    "plan_event_hash": plan_source["plan_event_hash"],
                    "plan_id": plan_id,
                }
                if any(binding.get(key) != value for key, value in expected.items()):
                    raise SharedQualificationStateError(
                        f"cross-chain terminal binding differs from source plan: {plan_id}"
                    )
                plan = _mapping(plan_source["plan"], "historical plan")
                if payload.get("experiment_family") != plan.get("experiment_family"):
                    raise SharedQualificationStateError(
                        f"terminal family differs from source plan: {plan_id}"
                    )
                if payload.get("study_identity") != plan.get("study_identity"):
                    raise SharedQualificationStateError(
                        f"terminal study identity differs from source plan: {plan_id}"
                    )
        open_by_family: dict[str, list[str]] = {}
        for plan_id, source in plan_sources.items():
            if plan_id in terminals:
                continue
            plan = _mapping(source["plan"], "historical plan")
            family = _required_text(plan.get("experiment_family"), "experiment family")
            open_by_family.setdefault(family, []).append(plan_id)
        return {
            "schema_version": 1,
            "repository_id": self.identity.repository_id,
            "catalog_sha256": hashlib.sha256(self.paths.catalog.read_bytes()).hexdigest(),
            "plan_count": len(plan_sources),
            "terminal_count": len(terminals),
            "open_plans_by_family": {
                family: sorted(plan_ids) for family, plan_ids in sorted(open_by_family.items())
            },
        }

    def close_imported_plan(
        self,
        plan_id: str,
        *,
        disposition: str,
        workflow_path: Path,
        impact_change_path: Path,
        approved_by: str,
        reason: str,
        now: datetime | None = None,
    ) -> str:
        """Append one separately approved administrative terminal for an imported plan."""
        plan_identity = _required_text(plan_id, "cross-chain plan identity")
        approver = _required_text(approved_by, "cross-chain terminal approver")
        concrete_reason = _required_text(reason, "cross-chain terminal reason")
        if disposition not in {"cancelled", "close-invalidated"}:
            raise SharedQualificationStateError("cross-chain disposition is invalid")
        required_capabilities = {
            SHARED_QUALIFICATION_STATE_CAPABILITY,
            CROSS_CHAIN_PLAN_ADMINISTRATION_CAPABILITY,
        }
        if disposition == "cancelled":
            required_capabilities.add(QUALIFICATION_PLAN_ABANDONMENT_CAPABILITY)
        authority = _require_effective_capabilities(workflow_path, required_capabilities)
        authority["capabilities"] = sorted(required_capabilities)
        impact = self._accepted_impact(
            impact_change_path,
            plan_id=plan_identity,
            disposition=disposition,
        )
        recorded_at = now or datetime.now(UTC)
        if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
            raise SharedQualificationStateError("cross-chain terminal clock must be timezone-aware")
        with locked_file(self.paths.migration_lock, self.lock_timeout_seconds):
            catalog = self._load_catalog()
            plan_source: dict[str, object] | None = None
            terminal_found = False
            for chain, source in self._registered_chains(catalog):
                state = QualificationRegistry(chain).read()
                for event in _events(state):
                    payload = _mapping(event.get("payload"), "qualification event payload")
                    if payload.get("plan_id") != plan_identity:
                        continue
                    if event.get("event_type") == "historical_plan":
                        if plan_source is not None:
                            raise SharedQualificationStateError(
                                "cross-chain plan identity appears in more than one chain"
                            )
                        if source.get("chain") != "shard":
                            raise SharedQualificationStateError(
                                "cross-chain administration only applies to imported plans"
                            )
                        plan_source = {
                            "payload": payload,
                            "event_hash": event.get("event_hash"),
                            **source,
                        }
                    elif event.get("event_type") in {
                        "historical_screen",
                        "historical_plan_abandoned",
                        "historical_plan_closed_invalidated",
                    }:
                        terminal_found = True
            if plan_source is None:
                raise SharedQualificationStateError(
                    f"imported historical plan is not registered: {plan_identity}"
                )
            if terminal_found:
                raise SharedQualificationStateError("imported historical plan is already terminal")
            plan = _mapping(plan_source["payload"], "historical plan")
            study_identity = _mapping(plan.get("study_identity"), "frozen study identity")
            study_path = _safe_relative_identity(
                study_identity.get("study_path"), "frozen study path"
            )
            from trading.workflow.studies import WorkflowStudyService

            lifecycle = WorkflowStudyService().lifecycle_identity(Path(study_path))
            expected_status = "cancelled" if disposition == "cancelled" else "paused"
            if lifecycle.get("status") != expected_status:
                raise SharedQualificationStateError(
                    f"cross-chain {disposition} requires a {expected_status} owning study"
                )
            if disposition == "close-invalidated":
                repository = WorkflowRepository(Path("workflows"))
                owner_version = Path("workflows") / (
                    f"{lifecycle['workflow']}--{lifecycle['workflow_version']}"
                )
                _registry, _slug, _version, record = repository._registered_version(
                    repository._resolve_input(owner_version)
                )
                if record.get("status") != "superseded":
                    raise SharedQualificationStateError(
                        "paused-plan invalidation requires a superseded owning workflow"
                    )
            active_state = QualificationRegistry(self.paths.active_registry).read()
            active_events = _events(active_state)
            active_head = (
                _required_sha256(active_events[-1].get("event_hash"), "active qualification head")
                if active_events
                else _GENESIS_HASH
            )
            payload: dict[str, object] = {
                "plan_id": plan_identity,
                "experiment_family": _required_text(
                    plan.get("experiment_family"), "historical plan experiment family"
                ),
                "study_identity": study_identity,
                "study_lifecycle": lifecycle,
                "source_binding": {
                    "registry_sha256": plan_source["registry_sha256"],
                    "head_hash": plan_source["head_hash"],
                    "plan_event_hash": plan_source["event_hash"],
                    "plan_id": plan_identity,
                },
                "authorization": authority,
                "accepted_impact": impact,
                "prior_shared": {
                    "catalog_sha256": hashlib.sha256(self.paths.catalog.read_bytes()).hexdigest(),
                    "active_event_count": len(active_events),
                    "active_head_hash": active_head,
                },
                "recorded_at": timestamp_text(recorded_at.astimezone(UTC)),
                "approved_by": approver,
                "reason": concrete_reason,
            }
            event_type = (
                "historical_plan_abandoned"
                if disposition == "cancelled"
                else "historical_plan_closed_invalidated"
            )
            event_id = QualificationRegistry(
                self.paths.active_registry
            ).append_cross_chain_terminal(
                event_type=event_type,
                payload=payload,
            )
            self.global_projection()
            return event_id

    def _discover_source_registries(self, logical_identity: str) -> set[Path]:
        relative = Path(logical_identity)
        return {
            candidate
            for root in self.identity.worktree_roots
            if (candidate := (root / relative).resolve()).is_file()
        }

    def _validate_source_is_quiescent(self, registry: Path) -> None:
        lock_path = registry.with_name(f".{registry.name}.lock")
        if _existing_lock_is_held(lock_path):
            raise SharedQualificationStateError(
                f"source registry mutation lock is held: {registry}"
            )
        journal = registry.with_name(f".{registry.name}.qualification-transaction.json")
        if journal.exists():
            raise SharedQualificationStateError(
                f"source qualification transaction journal is pending: {journal}"
            )

    def _load_catalog(self) -> dict[str, object]:
        try:
            catalog = json.loads(self.paths.catalog.read_bytes())
        except (OSError, json.JSONDecodeError) as exc:
            raise SharedQualificationStateError(
                f"cannot read shared authority catalog: {exc}"
            ) from exc
        if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
            raise SharedQualificationStateError("shared authority catalog is malformed")
        if catalog.get("repository_id") != self.identity.repository_id:
            raise SharedQualificationStateError(
                "shared authority catalog belongs to another repository"
            )
        logical_identity = _safe_relative_identity(
            catalog.get("logical_registry_identity"),
            "catalog logical registry identity",
        )
        raw_shards = catalog.get("shards")
        if not isinstance(raw_shards, list):
            raise SharedQualificationStateError("shared authority catalog shards are malformed")
        registered_sources = {
            _absolute_path(
                _mapping(shard, "catalog shard").get("source_registry_path"),
                "catalog source registry",
            )
            for shard in raw_shards
        }
        discovered_sources = self._discover_source_registries(logical_identity)
        if discovered_sources - registered_sources:
            raise SharedQualificationStateError(
                "shared authority catalog omits a discovered worktree qualification registry"
            )
        return catalog

    def _registered_chains(
        self, catalog: Mapping[str, object]
    ) -> list[tuple[Path, dict[str, object]]]:
        raw_shards = catalog.get("shards")
        if not isinstance(raw_shards, list):
            raise SharedQualificationStateError("shared authority catalog shards are malformed")
        chains: list[tuple[Path, dict[str, object]]] = []
        for raw_shard in raw_shards:
            shard = _mapping(raw_shard, "catalog shard")
            digest = _required_sha256(shard.get("registry_sha256"), "catalog registry digest")
            chain = self.paths.root / "shards" / digest / "qualification-registry.json"
            checkpoint = chain.with_name(f".{chain.name}.head.json")
            if hashlib.sha256(chain.read_bytes()).hexdigest() != digest:
                raise SharedQualificationStateError("immutable qualification shard digest mismatch")
            if hashlib.sha256(checkpoint.read_bytes()).hexdigest() != shard.get(
                "checkpoint_sha256"
            ):
                raise SharedQualificationStateError("immutable qualification checkpoint mismatch")
            chains.append(
                (
                    chain,
                    {
                        "registry_sha256": digest,
                        "head_hash": shard.get("head_hash"),
                        "chain": "shard",
                    },
                )
            )
        active = _mapping(catalog.get("active_chain"), "active chain catalog entry")
        if active.get("identity") != "active/qualification-registry.json":
            raise SharedQualificationStateError("active chain identity is malformed")
        chains.append(
            (
                self.paths.active_registry,
                {
                    "registry_sha256": hashlib.sha256(
                        self.paths.active_registry.read_bytes()
                    ).hexdigest(),
                    "head_hash": json.loads(self.paths.active_checkpoint.read_bytes())["head_hash"],
                    "chain": "active",
                },
            )
        )
        return chains

    def _verify_existing_decision(self, preview: MigrationPreview) -> None:
        catalog = self._load_catalog()
        if catalog != preview.catalog:
            raise SharedQualificationStateError(
                "existing shared authority differs from the approved migration decision"
            )
        self.global_projection()

    def _accepted_impact(
        self,
        change_path: Path,
        *,
        plan_id: str,
        disposition: str,
    ) -> dict[str, str]:
        path = Path(change_path).resolve()
        try:
            relative = path.relative_to(self.identity.repository_root).as_posix()
        except ValueError as exc:
            raise SharedQualificationStateError(
                "accepted impact change is outside the repository"
            ) from exc
        readme = read_markdown_document(path / "README.md")
        if readme.metadata.get("status") not in {"accepted", "released"}:
            raise SharedQualificationStateError("cross-chain closure requires accepted impact")
        impact_path = path / "IMPACT.md"
        decision_path = path / "DECISION.md"
        try:
            evidence_text = impact_path.read_text() + "\n" + decision_path.read_text()
        except OSError as exc:
            raise SharedQualificationStateError(
                f"cannot read accepted impact evidence: {exc}"
            ) from exc
        study_token = self._study_token_for_plan(plan_id)
        if disposition not in evidence_text or study_token not in evidence_text:
            raise SharedQualificationStateError(
                "accepted impact does not name the exact study and disposition"
            )
        return {
            "path": relative,
            "impact_sha256": hashlib.sha256(impact_path.read_bytes()).hexdigest(),
            "decision_sha256": hashlib.sha256(decision_path.read_bytes()).hexdigest(),
            "disposition": disposition,
        }

    def _study_token_for_plan(self, plan_id: str) -> str:
        for chain, _source in self._registered_chains(self._load_catalog()):
            for event in _events(QualificationRegistry(chain).read()):
                payload = _mapping(event.get("payload"), "qualification event payload")
                if (
                    event.get("event_type") != "historical_plan"
                    or payload.get("plan_id") != plan_id
                ):
                    continue
                study = _mapping(payload.get("study_identity"), "frozen study identity")
                path = _safe_relative_identity(study.get("study_path"), "frozen study path")
                version = next(
                    (
                        part.removeprefix("strategy-forward-replication-research--")
                        for part in Path(path).parts
                        if part.startswith("strategy-forward-replication-research--")
                    ),
                    None,
                )
                local = Path(path).name.rsplit("--", 1)[-1].upper()
                if not version or not local.startswith("S"):
                    raise SharedQualificationStateError("cannot derive exact study impact token")
                return f"{version}/{local}"
        raise SharedQualificationStateError(f"cannot find imported plan: {plan_id}")


def _require_declared_capability(
    workflow_path: Path,
    capability: str,
    *,
    require_effective: bool,
) -> None:
    workflow = Path(workflow_path).resolve()
    repository = WorkflowRepository(Path("workflows"))
    repository._require_structurally_valid()
    resolved = repository._resolve_input(workflow)
    if require_effective:
        repository.require_effective_version(resolved)
    release_path = resolved / "RELEASE.json"
    if release_path.is_file():
        payload = repository._read_json_object(release_path, label="workflow release")
        capabilities = payload.get("capabilities")
    else:
        capabilities = read_markdown_document(resolved / "README.md").metadata.get("capabilities")
    if not isinstance(capabilities, list) or capability not in capabilities:
        raise WorkflowAuthoringError(f"workflow does not declare required capability: {capability}")


def _require_effective_capabilities(workflow_path: Path, capabilities: set[str]) -> dict[str, str]:
    workflow = Path(workflow_path).resolve()
    repository = WorkflowRepository(Path("workflows"))
    repository._require_structurally_valid()
    resolved = repository._resolve_input(workflow)
    repository.require_effective_version(resolved)
    release_path = resolved / "RELEASE.json"
    payload = repository._read_json_object(release_path, label="workflow release")
    actual = payload.get("capabilities")
    if not isinstance(actual, list) or not capabilities.issubset(actual):
        raise WorkflowAuthoringError("effective workflow lacks shared qualification capability")
    return {
        "workflow": _required_text(payload.get("workflow"), "authorizing workflow"),
        "workflow_version": _required_text(payload.get("version"), "authorizing version"),
        "workflow_path": repository._repo_relative(resolved),
        "workflow_release_sha256": _sha256(release_path),
    }


def _git_output(repository_root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SharedQualificationStateError(
            f"cannot verify Git repository identity: {exc}"
        ) from exc
    output = result.stdout.strip()
    if not output:
        raise SharedQualificationStateError("Git repository identity command returned no output")
    return output


def _existing_lock_is_held(path: Path) -> bool:
    if not path.exists():
        return False
    descriptor = os.open(path, os.O_RDONLY)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        return False
    finally:
        os.close(descriptor)


def _write_exact(target: Path, source: Path, *, expected_sha256: str) -> None:
    content = source.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected_sha256:
        raise SharedQualificationStateError(
            f"source bytes changed after the approved migration preview: {source}"
        )
    atomic_write(target, content, replace=False)
    if target.read_bytes() != content:
        raise SharedQualificationStateError(f"staged shard differs from source bytes: {source}")


def _replay_registry_pair(
    registry_bytes: bytes,
    checkpoint_bytes: bytes,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="qualification-migration-preview-") as temporary:
        registry_path = Path(temporary) / "qualification-registry.json"
        registry_path.write_bytes(registry_bytes)
        registry_path.with_name(f".{registry_path.name}.head.json").write_bytes(checkpoint_bytes)
        return QualificationRegistry(registry_path).read()


def _events(state: Mapping[str, object]) -> list[dict[str, object]]:
    events = state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise SharedQualificationStateError("qualification registry events are malformed")
    return events


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SharedQualificationStateError(f"{label} is malformed")
    return dict(value)


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise SharedQualificationStateError(f"{label} is missing or non-canonical")
    return value


def _required_sha256(value: object, label: str) -> str:
    digest = _required_text(value, label)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise SharedQualificationStateError(f"{label} is not a canonical SHA-256 digest")
    return digest


def _safe_relative_identity(value: object, label: str) -> str:
    text = _required_text(value, label)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != text:
        raise SharedQualificationStateError(f"{label} is not a safe repository-relative path")
    return text


def _absolute_path(value: object, label: str) -> Path:
    text = _required_text(value, label)
    path = Path(text)
    if not path.is_absolute() or ".." in path.parts:
        raise SharedQualificationStateError(f"{label} must be an absolute canonical path")
    return path.resolve()

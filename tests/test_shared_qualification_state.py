from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from trading.core.accounting import canonical_json_bytes
from trading.research_data.evidence import QualificationEvidenceStore
from trading.research_data.qualification_registry import (
    QualificationRegistry,
    QualificationRegistryError,
)
from trading.research_data.shared_qualification_state import (
    DEFAULT_LOGICAL_REGISTRY_IDENTITY,
    MigrationSource,
    SharedMigrationRequest,
    SharedQualificationState,
    SharedQualificationStateError,
    resolve_workflow_qualification_registry_path,
)

WORKFLOW_V011 = Path("workflows/strategy-forward-replication-research--v011")
WORKFLOW_V010 = Path("workflows/strategy-forward-replication-research--v010")
GENESIS_HASH = "0" * 64


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_plan_registry(
    path: Path,
    *,
    plan_id: str,
    family: str,
    study_path: str | None = None,
) -> None:
    payload = {
        "plan_id": plan_id,
        "experiment_family": family,
        "definition_fingerprint": f"definition-{plan_id}",
    }
    if study_path is not None:
        payload["study_identity"] = {
            "study_path": study_path,
            "preregistration_sha256": "1" * 64,
            "plan_sha256": "2" * 64,
            "candidate_freeze_sha256": "3" * 64,
            "qualification_spec_sha256": "4" * 64,
            "workflow_release_sha256": "5" * 64,
        }
    content = {
        "sequence": 1,
        "event_id": f"historical-plan:{plan_id}",
        "event_type": "historical_plan",
        "payload": payload,
        "previous_hash": GENESIS_HASH,
    }
    event = {
        **content,
        "event_hash": hashlib.sha256(canonical_json_bytes(content)).hexdigest(),
    }
    registry_bytes = canonical_json_bytes({"schema_version": 1, "events": [event]})
    path.parent.mkdir(parents=True)
    path.write_bytes(registry_bytes)
    checkpoint = {
        "schema_version": 1,
        "event_count": 1,
        "registry_checksum": hashlib.sha256(registry_bytes).hexdigest(),
        "head_hash": event["event_hash"],
    }
    path.with_name(f".{path.name}.head.json").write_bytes(canonical_json_bytes(checkpoint))


@pytest.fixture
def split_repository(tmp_path: Path) -> tuple[Path, Path, Path]:
    main = tmp_path / "main"
    secondary = tmp_path / "secondary"
    main.mkdir()
    _git(main, "init")
    _git(main, "config", "user.email", "test@example.com")
    _git(main, "config", "user.name", "Test")
    (main / "README.md").write_text("test\n")
    _git(main, "add", "README.md")
    _git(main, "commit", "-m", "initial")
    _git(main, "worktree", "add", "-b", "secondary", str(secondary))
    main_registry = main / DEFAULT_LOGICAL_REGISTRY_IDENTITY
    secondary_registry = secondary / DEFAULT_LOGICAL_REGISTRY_IDENTITY
    _write_plan_registry(main_registry, plan_id="plan-main", family="family-a")
    _write_plan_registry(secondary_registry, plan_id="plan-secondary", family="family-a")
    return main, main_registry, secondary_registry


def _request(*registries: Path) -> SharedMigrationRequest:
    return SharedMigrationRequest(
        logical_registry_identity=DEFAULT_LOGICAL_REGISTRY_IDENTITY,
        approved_by="approver@example.com",
        sources=tuple(
            MigrationSource(
                registry,
                registry.with_name(f".{registry.name}.head.json"),
            )
            for registry in registries
        ),
    )


def test_worktrees_resolve_one_shared_authority_and_preview_global_conflict(
    split_repository: tuple[Path, Path, Path],
) -> None:
    main, main_registry, secondary_registry = split_repository
    main_state = SharedQualificationState(main)
    secondary_state = SharedQualificationState(secondary_registry.parents[1])

    assert main_state.paths == secondary_state.paths
    preview = main_state.preview_migration(
        _request(main_registry, secondary_registry),
        workflow_path=WORKFLOW_V011,
    )

    assert preview.open_plans_by_family == {"family-a": ("plan-main", "plan-secondary")}
    assert len(preview.decision_sha256) == 64
    assert not main_state.paths.root.exists()
    assert not main_state.paths.transaction_journal.exists()


def test_draft_capability_cannot_switch_runtime_while_v010_stays_local() -> None:
    repository_root = Path(".").resolve()

    assert (
        resolve_workflow_qualification_registry_path(
            repository_root,
            WORKFLOW_V010,
        )
        == repository_root / DEFAULT_LOGICAL_REGISTRY_IDENTITY
    )
    with pytest.raises(SharedQualificationStateError, match="release is required"):
        resolve_workflow_qualification_registry_path(
            repository_root,
            WORKFLOW_V011,
        )


def test_preview_rejects_incomplete_inventory(
    split_repository: tuple[Path, Path, Path],
) -> None:
    main, main_registry, secondary_registry = split_repository

    with pytest.raises(SharedQualificationStateError, match="inventory is not complete") as error:
        SharedQualificationState(main).preview_migration(
            _request(main_registry),
            workflow_path=WORKFLOW_V011,
        )

    assert str(secondary_registry) in str(error.value)


def test_preview_rejects_held_source_lock(
    split_repository: tuple[Path, Path, Path],
) -> None:
    main, main_registry, secondary_registry = split_repository
    lock_path = main_registry.with_name(f".{main_registry.name}.lock")
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(SharedQualificationStateError, match="mutation lock is held"):
            SharedQualificationState(main).preview_migration(
                _request(main_registry, secondary_registry),
                workflow_path=WORKFLOW_V011,
            )
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def test_apply_is_exact_and_replays_all_immutable_shards(
    split_repository: tuple[Path, Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main, main_registry, secondary_registry = split_repository
    state = SharedQualificationState(main)
    request = _request(main_registry, secondary_registry)
    preview = state.preview_migration(request, workflow_path=WORKFLOW_V011)
    monkeypatch.setattr(
        "trading.research_data.shared_qualification_state._require_effective_capabilities",
        lambda *_args, **_kwargs: {},
    )

    applied = state.apply_migration(
        request,
        workflow_path=WORKFLOW_V011,
        approved_decision_sha256=preview.decision_sha256,
    )

    assert applied == preview
    assert state.global_projection()["open_plans_by_family"] == {
        "family-a": ["plan-main", "plan-secondary"]
    }
    catalog = json.loads(state.paths.catalog.read_bytes())
    for shard in catalog["shards"]:
        source = Path(shard["source_registry_path"])
        imported = (
            state.paths.root / "shards" / shard["registry_sha256"] / "qualification-registry.json"
        )
        assert imported.read_bytes() == source.read_bytes()
    assert not state.paths.transaction_journal.exists()

    evidence = QualificationEvidenceStore(main.parent / "evidence")
    _evidence_path, evidence_digest = evidence.publish_shared(state)
    snapshot = evidence.resolve_shared(evidence_digest)
    assert snapshot.open_plans_by_family == {"family-a": ("plan-main", "plan-secondary")}

    recorded_at = datetime.now(UTC)
    active = QualificationRegistry(state.paths.active_registry, now=lambda: recorded_at)
    with pytest.raises(QualificationRegistryError, match="already has an open"):
        active._validate_plan_state_for_registration(
            active.read(),
            SimpleNamespace(
                plan_id="new-plan",
                experiment_family="family-a",
                created_at=recorded_at,
            ),
            "historical-plan:new-plan",
        )


def test_apply_rejects_a_different_approval_digest_before_publication(
    split_repository: tuple[Path, Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main, main_registry, secondary_registry = split_repository
    state = SharedQualificationState(main)
    monkeypatch.setattr(
        "trading.research_data.shared_qualification_state._require_effective_capabilities",
        lambda *_args, **_kwargs: {},
    )

    with pytest.raises(SharedQualificationStateError, match="does not match"):
        state.apply_migration(
            _request(main_registry, secondary_registry),
            workflow_path=WORKFLOW_V011,
            approved_decision_sha256="f" * 64,
        )

    assert not state.paths.root.exists()


def test_apply_recovers_only_the_exact_pending_decision(
    split_repository: tuple[Path, Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main, main_registry, secondary_registry = split_repository
    state = SharedQualificationState(main)
    request = _request(main_registry, secondary_registry)
    preview = state.preview_migration(request, workflow_path=WORKFLOW_V011)
    monkeypatch.setattr(
        "trading.research_data.shared_qualification_state._require_effective_capabilities",
        lambda *_args, **_kwargs: {},
    )
    with monkeypatch.context() as interrupted:
        interrupted.setattr(
            "trading.research_data.shared_qualification_state.os.replace",
            lambda *_args: (_ for _ in ()).throw(OSError("interrupted")),
        )
        with pytest.raises(OSError, match="interrupted"):
            state.apply_migration(
                request,
                workflow_path=WORKFLOW_V011,
                approved_decision_sha256=preview.decision_sha256,
            )
    assert state.paths.transaction_journal.exists()
    assert not state.paths.root.exists()

    state.apply_migration(
        request,
        workflow_path=WORKFLOW_V011,
        approved_decision_sha256=preview.decision_sha256,
    )

    assert state.paths.root.exists()
    assert not state.paths.transaction_journal.exists()


def test_cross_chain_invalidated_closure_binds_source_study_and_accepted_impact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init")
    _git(main, "config", "user.email", "test@example.com")
    _git(main, "config", "user.name", "Test")
    (main / "README.md").write_text("test\n")
    _git(main, "add", "README.md")
    _git(main, "commit", "-m", "initial")
    registry = main / DEFAULT_LOGICAL_REGISTRY_IDENTITY
    study_path = (
        "workflows/strategy-forward-replication-research--v008/work/studies/"
        "fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003"
    )
    _write_plan_registry(
        registry,
        plan_id="plan-paused",
        family="family-a",
        study_path=study_path,
    )
    state = SharedQualificationState(main)
    request = _request(registry)
    authority = {
        "workflow": "strategy-forward-replication-research",
        "workflow_version": "v011",
        "workflow_path": "workflows/strategy-forward-replication-research--v011",
        "workflow_release_sha256": "6" * 64,
    }
    monkeypatch.setattr(
        "trading.research_data.shared_qualification_state._require_effective_capabilities",
        lambda *_args, **_kwargs: authority.copy(),
    )
    preview = state.preview_migration(request, workflow_path=WORKFLOW_V011)
    state.apply_migration(
        request,
        workflow_path=WORKFLOW_V011,
        approved_decision_sha256=preview.decision_sha256,
    )
    monkeypatch.setattr(
        "trading.workflow.studies.WorkflowStudyService.lifecycle_identity",
        lambda _self, _path: {
            "study_path": study_path,
            "workflow": "strategy-forward-replication-research",
            "workflow_version": "v008",
            "status": "paused",
        },
    )
    impact = main / "workflows" / "accepted-change"
    impact.mkdir(parents=True)
    (impact / "README.md").write_text("---\nstatus: accepted\n---\n")
    (impact / "IMPACT.md").write_text("v008/S003 close-invalidated\n")
    (impact / "DECISION.md").write_text("accepted v008/S003 close-invalidated\n")

    event_id = state.close_imported_plan(
        "plan-paused",
        disposition="close-invalidated",
        workflow_path=WORKFLOW_V011,
        impact_change_path=impact,
        approved_by="approver@example.com",
        reason="superseded workflow invalidated the prior continuation route",
    )

    assert event_id == "historical-plan-closed-invalidated:plan-paused"
    projection = state.global_projection()
    assert projection["terminal_count"] == 1
    assert projection["open_plans_by_family"] == {}
    evidence = QualificationEvidenceStore(main.parent / "terminal-evidence")
    _path, digest = evidence.publish_shared(state)
    assert evidence.resolve_shared(digest).open_plans_by_family == {}

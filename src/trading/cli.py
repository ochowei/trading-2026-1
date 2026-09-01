"""
統一 CLI 入口 (Unified CLI Entry Point)
支援實驗、跟單與分析子命令。
Supports experiment, followup, and analysis subcommands.
"""

import argparse
import json
import logging
import sys
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from trading.commands import legacy as legacy_commands
from trading.commands import research as research_commands
from trading.commands import workflow as workflow_commands
from trading.commands.research import cmd_research
from trading.commands.workflow import cmd_workflow
from trading.core.data_fetcher import create_default_market_data_service
from trading.core.followup_cutover import (
    FollowupActivationProof,
    FollowupActivationVerifier,
    FollowupLifecycleRegistry,
    FollowupShadowProof,
    FollowupShadowVerifier,
    FollowupStrategy,
)
from trading.core.manual_ledger import (
    CASH_EVENT_TYPES,
    FILL_EVENT_TYPES,
    RECORDABLE_EVENT_TYPES,
    LedgerError,
    LedgerEvent,
    LedgerInitialization,
    ManualLedgerStore,
)
from trading.core.policy_authoring import PolicyAuthoringError, PolicyRepository
from trading.core.proposals import ProposalTerms
from trading.legacy.definition_resolver import resolve_current_definition_fingerprint
from trading.legacy.results import inspect_result
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataCoveragePolicy,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.research_data import (
    ExperimentTrialRegistry,
    QualificationEvidenceStore,
    QualificationRegistry,
    ResearchDataStore,
    ResearchDefinitionStore,
    SharedMigrationRequest,
    SharedQualificationState,
    qualification_evidence_directory,
    resolve_study_qualification_registry_path,
    resolve_workflow_qualification_registry_path,
    trial_registry_path,
)
from trading.workflow.challenge_execution import run_fixed_study_challenges
from trading.workflow.qualification import (
    LEGACY_QUALIFICATION_RETIREMENT_MESSAGE,
    register_forward_qualification_plan,
    run_registered_historical_screen,
)
from trading.workflow.qualification_plan_abandonment import (
    resolve_qualification_plan_abandonment_authority,
)
from trading.workflow.retrospective_replay import run_fixed_calendar_retrospective_replay
from trading.workflow.studies import WorkflowStudyService
from trading.workflow.study_qualification import (
    STUDY_QUALIFICATION_CAPABILITY,
    compile_study_qualification_plan,
)

# 設定日誌格式 (Configure logging format)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

LEGACY_EXPERIMENT_RETIREMENT_MESSAGE = legacy_commands.RETIREMENT_MESSAGE

DEFAULT_MANUAL_LEDGER_PATH = Path("state/manual-execution-ledger.csv")
DEFAULT_RECONCILIATION_PATH = Path("state/manual-reconciliation.json")
DEFAULT_QUALIFICATION_REGISTRY_PATH = Path("state/qualification-registry.json")
DEFAULT_FOLLOWUP_LIFECYCLE_PATH = Path("state/followup-lifecycle.json")
DEFAULT_LIVE_DRIFT_PATH = Path("state/live-drift")


def create_default_research_data_store() -> ResearchDataStore:
    """Build the local protected immutable research-data store."""
    return ResearchDataStore(Path(".research-data/blobs"))


def create_default_research_definition_store() -> ResearchDefinitionStore:
    """Build the local protected immutable research-definition store."""
    return ResearchDefinitionStore(Path(".research-data/blobs"))


def cmd_qualification_status(args: argparse.Namespace) -> None:
    """Show persisted historical and Shadow lifecycle without changing it."""
    state = QualificationRegistry(args.path).read()
    raw_events = state.get("events")
    events = raw_events if isinstance(raw_events, list) else []
    if not events:
        print("qualification registry: empty")
        return
    screens = {
        payload.get("plan_id"): payload
        for event in events
        if isinstance(event, Mapping)
        and event.get("event_type") == "historical_screen"
        and isinstance((payload := event.get("payload")), Mapping)
    }
    abandonments = {
        payload.get("plan_id"): payload
        for event in events
        if isinstance(event, Mapping)
        and event.get("event_type") == "historical_plan_abandoned"
        and isinstance((payload := event.get("payload")), Mapping)
    }
    for event in events:
        if not isinstance(event, Mapping) or event.get("event_type") != "historical_plan":
            continue
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            continue
        plan_id = payload.get("plan_id")
        screen = screens.get(plan_id, {})
        abandonment = abandonments.get(plan_id, {})
        disposition = (
            "historical-plan-abandoned"
            if abandonment
            else screen.get("disposition", "historical-screen-pending")
        )
        print(f"{plan_id}: {disposition}")
        print(f"  definition fingerprint: {payload.get('definition_fingerprint', '-')}")
        if abandonment:
            print(
                f"  abandoned at: {abandonment.get('abandoned_at', '-')} "
                f"by {abandonment.get('approved_by', '-')}"
            )
            print(f"  reason: {abandonment.get('reason', '-')}")
    for event in events:
        if not isinstance(event, Mapping) or event.get("event_type") != "shadow_registration":
            continue
        registration = event.get("payload")
        if not isinstance(registration, Mapping):
            continue
        shadow_id = registration.get("shadow_id")
        evidence = next(
            (
                item.get("payload")
                for item in reversed(events)
                if isinstance(item, Mapping)
                and item.get("event_type") == "shadow_evidence"
                and isinstance(item.get("payload"), Mapping)
                and item["payload"].get("shadow_id") == shadow_id
            ),
            {},
        )
        activation = next(
            (
                item.get("payload")
                for item in reversed(events)
                if isinstance(item, Mapping)
                and item.get("event_type") == "activation_evaluation"
                and isinstance(item.get("payload"), Mapping)
                and item["payload"].get("shadow_id") == shadow_id
                and item["payload"].get("evaluated_at") == evidence.get("as_of")
            ),
            {},
        )
        disposition = activation.get(
            "disposition",
            "shadow-awaiting-activation" if evidence else "shadow-awaiting-evidence",
        )
        fills = evidence.get("simulated_fills", [])
        trades = len(fills) if isinstance(fills, list) else 0
        authorization = activation.get("authorized_for_live_orders", False)
        print(f"{shadow_id}: {disposition}")
        print(
            f"  sessions={evidence.get('completed_sessions', 0)} trades={trades} "
            f"live authorization={str(authorization).lower()}"
        )


def cmd_qualification_shared_state(args: argparse.Namespace) -> None:
    """Inspect or migrate the Git-common qualification authority."""
    shared = SharedQualificationState(args.repository_root)
    if args.shared_state_command == "status":
        projection = shared.global_projection()
        print(json.dumps(projection, indent=2, sort_keys=True))
        return
    if args.shared_state_command == "evidence-snapshot":
        path, digest = QualificationEvidenceStore(args.output_root).publish_shared(shared)
        print(f"shared qualification evidence published: {digest}")
        print(f"  path: {path}")
        return
    if args.shared_state_command == "close-plan":
        event_id = shared.close_imported_plan(
            args.plan_id,
            disposition=args.disposition,
            workflow_path=args.workflow,
            impact_change_path=args.impact_change,
            approved_by=args.approved_by,
            reason=args.reason,
        )
        print(f"shared qualification plan closed: {event_id}")
        return
    request = SharedMigrationRequest.from_path(args.request)
    if args.shared_state_command == "migration-preview":
        preview = shared.preview_migration(request, workflow_path=args.workflow)
        print(json.dumps(preview.as_payload(), indent=2, sort_keys=True))
        return
    if args.shared_state_command == "migration-apply":
        preview = shared.apply_migration(
            request,
            workflow_path=args.workflow,
            approved_decision_sha256=args.approved_decision_sha256,
        )
        print(f"shared qualification migration published: {preview.decision_sha256}")
        print(f"  shared root: {preview.shared_paths.root}")


def cmd_qualification_plan_register(args: argparse.Namespace) -> None:
    """Freeze and append one forward-dated qualification plan."""
    if args.experiment:
        raise SystemExit(LEGACY_QUALIFICATION_RETIREMENT_MESSAGE)
    if args.workflow is not None:
        release_path = Path(args.workflow) / "RELEASE.json"
        try:
            release = json.loads(release_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            release = {}
        if isinstance(release, dict) and STUDY_QUALIFICATION_CAPABILITY in release.get(
            "capabilities", []
        ):
            raise ValueError(
                "capability-scoped workflow qualification requires "
                "`qualification plan register-study --study ...`"
            )
    if (
        args.family_research
        or args.evidence_role == "study-time-retrospective"
        or (args.evidence_role == "historical" and args.development_years is not None)
    ):
        raise ValueError(
            "complete-family, study-time, and explicit clean calendars require "
            "`qualification plan register-study --study ...`"
        )
    family_source_sha256: dict[str, str] = {}
    for assignment in args.family_source_sha or ():
        identity, separator, digest = assignment.partition("=")
        if separator != "=" or not identity.strip() or not digest.strip():
            raise ValueError("--family-source-sha must use IDENTITY=SHA256")
        identity = identity.strip()
        if identity in family_source_sha256:
            raise ValueError(f"duplicate family source digest: {identity}")
        family_source_sha256[identity] = digest.strip()
    qualification_path = args.path
    if args.workflow is not None and args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_workflow_qualification_registry_path(
            Path("."),
            args.workflow,
        )
    plan = register_forward_qualification_plan(
        experiment_name=args.experiment,
        research_identity=args.research,
        workflow_path=args.workflow,
        family_baseline_trial_id=args.family_baseline_trial_id,
        evaluation_years=tuple(args.evaluation_years),
        maximum_holding_sessions=args.maximum_holding_sessions,
        execution_lag_sessions=args.execution_lag_sessions,
        dependency_sessions=args.dependency_sessions,
        embargo_sessions=args.embargo_sessions,
        stress_drawdown_limit=args.stress_drawdown_limit,
        random_seed=args.random_seed,
        random_samples=args.random_samples,
        bootstrap_repetitions=args.bootstrap_repetitions,
        bootstrap_block_sessions=args.bootstrap_block_sessions,
        qualification_registry_path=qualification_path,
        trial_registry_path=args.trial_registry_path,
        evidence_role=args.evidence_role,
        evidence_classification=args.evidence_classification,
        evidence_justification=args.audit_justification,
        trial_history_complete=args.trial_history_complete,
        development_years=(
            tuple(args.development_years) if args.development_years is not None else None
        ),
        warmup_start=args.warmup_start,
        warmup_end=args.warmup_end,
        quarantine_years=(
            tuple(args.quarantine_years) if args.quarantine_years is not None else None
        ),
        family_research_identities=tuple(args.family_research or ()),
        dry_run=args.dry_run,
        family_source_sha256=family_source_sha256,
        maximum_family_trials=args.family_trial_budget,
    )
    epoch = plan.forward_selection_epoch or getattr(
        plan,
        "retrospective_selection_checkpoint",
        None,
    )
    action = "compiled (dry-run)" if args.dry_run else "registered"
    print(f"qualification plan {action}: {plan.plan_id}")
    print(f"  family: {plan.experiment_family}")
    print(f"  first evaluation session: {plan.evaluation_sessions[0].isoformat()}")
    print(f"  last evaluation session: {plan.evaluation_sessions[-1].isoformat()}")
    print(f"  selected trial: {epoch.selected_trial_id if epoch else '-'}")
    print(f"  frozen family trials: {len(epoch.included_trial_ids) if epoch else 0}")
    print(
        "  prior selection history incomplete: "
        f"{str(epoch.prior_selection_history_incomplete).lower() if epoch else 'false'}"
    )
    print(f"  evidence role: {getattr(plan, 'evidence_role', 'historical')}")
    evidence_audit = getattr(plan, "evidence_audit", None)
    print(
        "  evidence classification: "
        f"{evidence_audit.classification if evidence_audit else 'legacy-unspecified'}"
    )


def cmd_qualification_plan_register_study(args: argparse.Namespace) -> None:
    """Compile or register one exact frozen study without caller-supplied study inputs."""
    qualification_path = args.path
    if args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_study_qualification_registry_path(args.study)
    plan = compile_study_qualification_plan(
        study_path=args.study,
        qualification_registry_path=qualification_path,
        trial_registry_path=args.trial_registry_path,
        dry_run=args.dry_run,
        approved_by=args.approved_by,
        contamination_declaration=args.contamination_declaration,
    )
    boundary = plan.forward_selection_epoch or plan.retrospective_selection_checkpoint
    action = "compiled (dry-run)" if args.dry_run else "registered"
    print(f"study qualification plan {action}: {plan.plan_id}")
    print(f"  study: {plan.study_identity.study_path if plan.study_identity else '-'}")
    print(f"  family: {plan.experiment_family}")
    print(f"  frozen family trials: {len(boundary.included_trial_ids) if boundary else 0}")
    print(f"  evidence role: {plan.evidence_role}")


def cmd_qualification_plan_abandon(args: argparse.Namespace) -> None:
    """Append one authorized terminal event for a cancelled study's open plan."""
    authority = resolve_qualification_plan_abandonment_authority(args.workflow)
    studies = WorkflowStudyService()
    qualification_path = args.path
    if args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_workflow_qualification_registry_path(
            Path("."),
            args.workflow,
        )
    event_id = QualificationRegistry(qualification_path).abandon_historical_plan(
        args.plan_id,
        approved_by=args.approved_by,
        reason=args.reason,
        study_identity_resolver=lambda study_path: studies.lifecycle_identity(Path(study_path)),
        authorization=authority.as_payload(),
    )
    print(f"qualification plan abandoned: {event_id}")
    print(f"  authority: {authority.workflow}@{authority.workflow_version}")
    print("  outcome authority: none")


def cmd_qualification_evidence_snapshot(args: argparse.Namespace) -> None:
    """Publish one verified immutable qualification-registry snapshot."""
    path, digest = QualificationEvidenceStore(args.output_root).publish_registry(
        args.path,
        repository_root=Path.cwd(),
        source_registry_identity=args.source_registry_identity,
    )
    print(f"qualification evidence published: {path}")
    print(f"  sha256: {digest}")


def cmd_qualification_screen_run(args: argparse.Namespace) -> None:
    """Recompute and record a completed frozen Historical Screen."""
    trial_manifests: dict[str, Path] = {}
    for assignment in args.trial:
        experiment, separator, manifest = assignment.partition("=")
        if separator != "=" or not experiment.strip() or not manifest.strip():
            raise ValueError("--trial must use EXPERIMENT=MANIFEST")
        experiment = experiment.strip()
        if experiment in trial_manifests:
            raise ValueError(f"duplicate screen experiment: {experiment}")
        trial_manifests[experiment] = Path(manifest.strip())
    qualification_path = args.path
    if args.workflow is not None and args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_workflow_qualification_registry_path(
            Path("."),
            args.workflow,
        )
    execution = run_registered_historical_screen(
        plan_id=args.plan_id,
        trial_manifests=trial_manifests,
        qualification_registry_path=qualification_path,
        trial_registry_path=args.trial_registry_path,
        research_data_store=create_default_research_data_store(),
        definition_store=create_default_research_definition_store(),
        workflow_path=args.workflow,
    )
    print(f"historical screen recorded: {execution.event_id}")
    print(f"  disposition: {execution.screen.disposition}")
    print(f"  passed: {str(execution.screen.passed).lower()}")


def cmd_qualification_replay_run_study(args: argparse.Namespace) -> None:
    """Run the fixed 2025 provider-free replay without granting operational authority."""
    qualification_path = args.path
    if args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_study_qualification_registry_path(args.study)
    publication = run_fixed_calendar_retrospective_replay(
        study_path=args.study,
        plan_id=args.plan_id,
        selected_manifest_path=args.manifest,
        challenge_manifest_path=args.challenge_manifest,
        qualification_registry_path=qualification_path,
        trial_registry_path=args.trial_registry_path,
        research_data_store=create_default_research_data_store(),
        definition_store=create_default_research_definition_store(),
        output_root=args.output_root,
        dry_run=args.dry_run,
    )
    action = "validated (dry-run)" if args.dry_run else "published"
    print(f"retrospective execution replay {action}: {publication.replay_id}")
    print(f"  path: {publication.replay_path}")
    print(f"  passed: {str(publication.passed).lower()}")
    print("  authority: non-actionable-historical-replay-only")


def cmd_qualification_challenge_run_study(args: argparse.Namespace) -> None:
    """Run the independent challenge-only operation from exact formal artifacts."""
    family_manifests: dict[str, Path] = {}
    for assignment in args.trial:
        identity, separator, manifest = assignment.partition("=")
        if separator != "=" or not identity.strip() or not manifest.strip():
            raise ValueError("--trial must use IDENTITY=MANIFEST")
        identity = identity.strip()
        if identity in family_manifests:
            raise ValueError(f"duplicate challenge trial identity: {identity}")
        family_manifests[identity] = Path(manifest.strip())
    qualification_path = args.path
    if args.path == DEFAULT_QUALIFICATION_REGISTRY_PATH:
        qualification_path = resolve_study_qualification_registry_path(args.study)
    manifest_path = run_fixed_study_challenges(
        study_path=args.study,
        plan_id=args.plan_id,
        family_manifests=family_manifests,
        qualification_registry_path=qualification_path,
        trial_registry_path=args.trial_registry_path,
        research_data_store=create_default_research_data_store(),
        output_root=args.output_root,
        dry_run=args.dry_run,
    )
    action = "validated (dry-run)" if args.dry_run else "published"
    print(f"fixed-calendar challenges {action}: {manifest_path}")
    print("  artifacts: 9")
    print("  authority: challenge-only")


def cmd_qualification(args: argparse.Namespace) -> None:
    """Dispatch qualification lifecycle workflows."""
    try:
        if args.qualification_command == "status":
            cmd_qualification_status(args)
        elif args.qualification_command == "plan" and args.plan_command == "register":
            cmd_qualification_plan_register(args)
        elif args.qualification_command == "plan" and args.plan_command == "register-study":
            cmd_qualification_plan_register_study(args)
        elif args.qualification_command == "plan" and args.plan_command == "abandon":
            cmd_qualification_plan_abandon(args)
        elif args.qualification_command == "shared-state":
            cmd_qualification_shared_state(args)
        elif args.qualification_command == "evidence-snapshot":
            cmd_qualification_evidence_snapshot(args)
        elif args.qualification_command == "screen" and args.screen_command == "run":
            cmd_qualification_screen_run(args)
        elif args.qualification_command == "challenge" and args.challenge_command == "run-study":
            cmd_qualification_challenge_run_study(args)
        elif args.qualification_command == "replay" and args.replay_command == "run-study":
            cmd_qualification_replay_run_study(args)
    except (KeyError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"qualification error: {exc}") from exc


def cmd_policy(args: argparse.Namespace) -> None:
    """Dispatch tracked policy validation, synchronization, and release preparation."""
    repository = PolicyRepository(args.root)
    try:
        if args.policy_command == "validate":
            if args.all and args.path is not None:
                raise PolicyAuthoringError("validate accepts a path or --all, not both")
            issues = repository.validate_all()
            if issues:
                for issue in issues:
                    print(f"FAIL {issue}")
                raise SystemExit(f"policy validation failed: {len(issues)} issue(s)")
            print("policy validation passed")
        elif args.policy_command == "sync":
            repository.sync()
            print("policy indexes synchronized")
        elif args.policy_command == "version":
            repository.transition_version(
                args.path,
                args.status,
                approved_by=args.approved_by,
            )
            print(f"policy version transitioned to {args.status}: {args.path}")
        elif args.policy_command == "release":
            release = repository.release(args.path, approved_by=args.approved_by)
            print(f"policy release prepared: {release['policy']}@{release['version']}")
            print("  becomes effective only after merge to the canonical branch")
    except PolicyAuthoringError as exc:
        raise SystemExit(f"policy error: {exc}") from exc


def cmd_followup_state(args: argparse.Namespace) -> None:
    """Manage the local controlled-cutover lifecycle without placing orders."""
    from trading.followup import STRATEGIES

    try:
        registry = FollowupLifecycleRegistry(args.path)
        if args.followup_state_command in {"init", "resume", "activate", "shadow"}:
            raise SystemExit(LEGACY_EXPERIMENT_RETIREMENT_MESSAGE)
        if args.followup_state_command == "init":
            store = ManualLedgerStore(args.ledger_path)
            replay = store.verify()
            strategies = tuple(
                FollowupStrategy(
                    str(item["ticker"]),
                    str(item["experiment_name"]),
                )
                for item in STRATEGIES
            )
            expected_universe = {strategy.ticker for strategy in strategies}
            if set(replay.universe) != expected_universe:
                raise ValueError("ledger universe does not match the followup universe")
            if not store.reconciliation_is_current(args.reconciliation_path):
                raise ValueError("broker reconciliation is missing, failed, or stale")
            explicit_owners: dict[str, FollowupStrategy] = {}
            for assignment in args.position_owner or ():
                ticker, separator, experiment = assignment.partition("=")
                ticker = ticker.strip().upper()
                experiment = experiment.strip()
                if separator != "=" or not ticker or not experiment:
                    raise ValueError("position owner must use TICKER=EXPERIMENT")
                explicit_owners[ticker] = FollowupStrategy(ticker, experiment)
            position_owners: dict[str, FollowupStrategy] = {}
            for (ticker, _instrument), position in replay.positions.items():
                proposal = replay.proposals.get(position.entry_proposal_id)
                recorded_owner = (
                    proposal.authorization.get("strategy_id") if proposal is not None else None
                )
                if isinstance(recorded_owner, str) and recorded_owner.strip():
                    position_owners[ticker] = FollowupStrategy(ticker, recorded_owner)
                elif ticker in explicit_owners:
                    position_owners[ticker] = explicit_owners[ticker]
                else:
                    raise ValueError(
                        f"open position {ticker} requires --position-owner {ticker}=EXPERIMENT"
                    )
            lifecycle_strategies = tuple(
                sorted(
                    {*strategies, *position_owners.values()},
                    key=lambda item: (item.ticker, item.experiment_name),
                )
            )
            state = registry.initialize_cutover(
                lifecycle_strategies,
                occurred_at=args.timestamp or datetime.now(UTC),
                position_owners=position_owners,
            )
            print(
                "controlled followup cutover initialized: "
                f"{len(state.strategies)} Legacy Active strategies; new entries paused"
            )
            return
        if args.followup_state_command == "status":
            state = registry.read()
            mode = "paused" if state.no_new_entry else "eligible Active strategies only"
            print(f"new entries: {mode}")
            for strategy, lifecycle in state.strategies:
                print(f"{strategy.ticker}/{strategy.experiment_name}: {lifecycle.value}")
            return
        if args.followup_state_command in {"pause", "resume"}:
            state = registry.set_no_new_entry(
                args.followup_state_command == "pause",
                occurred_at=args.timestamp or datetime.now(UTC),
                reason=args.reason,
            )
            mode = "paused" if state.no_new_entry else "eligible Active strategies only"
            print(f"new entries: {mode}")
            return
        if args.followup_state_command == "activate":
            from trading.core.live_drift_registry import (
                LiveDriftRegistry,
                verify_envelope_qualification_sources,
            )

            strategy = FollowupStrategy(args.ticker, args.experiment)
            if not args.drift_envelope_id:
                raise ValueError("activation requires a frozen --drift-envelope-id")

            def current_result_fingerprint(item: FollowupStrategy) -> str:
                record = inspect_result(
                    item.experiment_name,
                    current_definition_fingerprint=resolve_current_definition_fingerprint(
                        item.experiment_name
                    ),
                )
                if record is None or record.validity.status.value != "valid":
                    raise ValueError("current persisted result is not valid")
                fingerprint = record.result.payload.get("definition_fingerprint")
                if not isinstance(fingerprint, str):
                    raise ValueError("current valid result fingerprint is missing")
                return fingerprint

            qualification_registry = QualificationRegistry(args.qualification_path)
            verifier = FollowupActivationVerifier(
                qualification_registry=qualification_registry,
                lifecycle_registry=registry,
                current_result_fingerprint_resolver=current_result_fingerprint,
                trial_registry=ExperimentTrialRegistry(trial_registry_path()),
            )
            drift_registry = LiveDriftRegistry(args.drift_path)

            def verify_drift_activation(
                item: FollowupStrategy,
                proof: FollowupActivationProof,
                _activation_event_id: str,
            ) -> None:
                drift_state = drift_registry.read()
                envelope = drift_state.envelope
                if envelope is None or envelope.envelope_id != proof.drift_envelope_id:
                    raise ValueError("frozen drift envelope is missing or does not match proof")
                if envelope.strategy_id != f"{item.ticker}/{item.experiment_name}":
                    raise ValueError("frozen drift envelope strategy identity does not match")
                if envelope.definition_fingerprint != proof.result_fingerprint:
                    raise ValueError("frozen drift envelope definition does not match result")
                verify_envelope_qualification_sources(
                    envelope,
                    qualification_state=qualification_registry.read(),
                    shadow_id=proof.shadow_id,
                    activation_event_id=proof.qualification_event_id,
                )
                if drift_state.activation_event_id is not None:
                    raise ValueError("drift envelope is already bound to an activation")

            writer = FollowupLifecycleRegistry(
                args.path,
                activation_verifier=verifier,
                drift_activation_verifier=verify_drift_activation,
                coordination_lock_path=drift_registry.coordination_lock_path,
            )
            state = writer.activate_strategy(
                strategy,
                proof=FollowupActivationProof(
                    shadow_id=args.shadow_id,
                    qualification_event_id=args.qualification_event_id,
                    result_fingerprint=args.result_fingerprint,
                    parity_digest=args.parity_digest,
                    drift_envelope_id=args.drift_envelope_id,
                ),
                occurred_at=args.timestamp or datetime.now(UTC),
                reason=args.reason,
            )
            activation_event = next(
                event
                for event in reversed(state.events)
                if event.get("event_type") == "strategy_activated"
                and isinstance(event.get("payload"), Mapping)
                and event["payload"].get("ticker") == strategy.ticker
                and event["payload"].get("experiment_name") == strategy.experiment_name
            )
            drift_registry.bind_activation(
                strategy_id=f"{strategy.ticker}/{strategy.experiment_name}",
                envelope_id=args.drift_envelope_id,
                activation_event_id=str(activation_event["event_id"]),
                occurred_at=args.timestamp or datetime.now(UTC),
            )
            lifecycle = state.status_for(strategy.ticker, strategy.experiment_name)
            print(f"{strategy.ticker}/{strategy.experiment_name}: {lifecycle.value}")
            return
        if args.followup_state_command == "shadow":
            strategy = FollowupStrategy(args.ticker, args.experiment)

            def current_result_fingerprint(item: FollowupStrategy) -> str:
                record = inspect_result(
                    item.experiment_name,
                    current_definition_fingerprint=resolve_current_definition_fingerprint(
                        item.experiment_name
                    ),
                )
                if record is None or record.validity.status.value != "valid":
                    raise ValueError("current persisted result is not valid")
                fingerprint = record.result.payload.get("definition_fingerprint")
                if not isinstance(fingerprint, str):
                    raise ValueError("current valid result fingerprint is missing")
                return fingerprint

            verifier = FollowupShadowVerifier(
                qualification_registry=QualificationRegistry(args.qualification_path),
                lifecycle_registry=registry,
                current_result_fingerprint_resolver=current_result_fingerprint,
                trial_registry=ExperimentTrialRegistry(trial_registry_path()),
            )
            writer = FollowupLifecycleRegistry(args.path, shadow_verifier=verifier)
            state = writer.register_shadow_strategy(
                strategy,
                proof=FollowupShadowProof(
                    shadow_id=args.shadow_id,
                    registration_event_id=args.registration_event_id,
                    historical_screen_event_id=args.historical_screen_event_id,
                    result_fingerprint=args.result_fingerprint,
                    parity_digest=args.parity_digest,
                ),
                occurred_at=args.timestamp or datetime.now(UTC),
                reason=args.reason,
            )
            print(f"{strategy.ticker}/{strategy.experiment_name}: shadow")
            return
        if args.followup_state_command in {"retire", "complete-retirement"}:
            strategy = FollowupStrategy(args.ticker, args.experiment)
            store = ManualLedgerStore(args.ledger_path)
            if not store.reconciliation_is_current(args.reconciliation_path):
                raise ValueError("broker reconciliation is missing, failed, or stale")

            def has_actual_position(item: FollowupStrategy) -> bool:
                replay = store.verify()
                return (item.ticker, item.ticker) in replay.positions

            def has_outstanding_entry(item: FollowupStrategy) -> bool:
                replay = store.verify()
                return bool(
                    replay.outstanding_entries(
                        sleeve_id=item.ticker,
                        instrument=item.ticker,
                    )
                )

            writer = FollowupLifecycleRegistry(
                args.path,
                actual_position_resolver=has_actual_position,
                outstanding_entry_resolver=has_outstanding_entry,
                ledger_head_resolver=lambda: store.verify().head_hash,
            )
            operation = (
                writer.retire_strategy
                if args.followup_state_command == "retire"
                else writer.complete_retirement
            )
            state = operation(
                strategy,
                occurred_at=args.timestamp or datetime.now(UTC),
                reason=args.reason,
            )
            lifecycle = state.status_for(strategy.ticker, strategy.experiment_name)
            print(f"{strategy.ticker}/{strategy.experiment_name}: {lifecycle.value}")
            return
        raise ValueError(f"unsupported followup-state command: {args.followup_state_command}")
    except (LedgerError, OSError, TypeError, ValueError) as exc:
        print(f"followup-state error: {exc}")
        raise SystemExit(1) from exc


def cmd_drift(args: argparse.Namespace) -> None:
    """Manage private Phase 8 evidence without broker or live-order access."""
    from trading.core.live_drift import DriftMetricKind, DriftObservation, HardGuardKind
    from trading.core.live_drift_registry import (
        LiveDriftRegistry,
        LiveDriftRegistryError,
        verified_shadow_trade_total,
    )

    registry_kwargs: dict[str, object] = {}
    if args.drift_command == "observe" and args.shadow_evidence_event_id:

        def verify_shadow_trades(envelope, observation) -> bool:
            expected = verified_shadow_trade_total(
                envelope,
                qualification_state=QualificationRegistry(args.qualification_path).read(),
                evidence_event_id=args.shadow_evidence_event_id,
                session=observation.session,
            )
            return (
                observation.completed_shadow_trades_total == expected
                and args.shadow_evidence_event_id in observation.source_identities
            )

        registry_kwargs["shadow_trade_verifier"] = verify_shadow_trades
    if args.drift_command in {"clean-check", "recover"}:
        store = ManualLedgerStore(args.ledger_path)

        def verified_integrity() -> tuple[bool, str]:
            try:
                replay = store.verify()
            except LedgerError:
                return False, ""
            return store.reconciliation_is_current(args.reconciliation_path), replay.accounting_hash

        def verify_clean_check(_session: date, evidence_identity: str) -> bool:
            reconciled, accounting_hash = verified_integrity()
            return reconciled and evidence_identity == accounting_hash

        registry_kwargs = {
            "clean_check_verifier": verify_clean_check,
            "hard_guard_verifier": lambda: verified_integrity()[0],
        }
    registry = LiveDriftRegistry(args.path, **registry_kwargs)
    try:
        if args.drift_command == "status":
            state = registry.read()
            print(f"drift state: {state.state.value}")
            print(f"buy allowed: {state.buy_allowed}")
            print(f"envelope: {state.envelope.envelope_id if state.envelope else '-'}")
            print(f"activation: {state.activation_event_id or '-'}")
            print(f"observations: {len(state.observations)}")
            print(f"checkpoints: {len(state.checkpoints)}")
            if state.pause_session is not None:
                print(f"paused since: {state.pause_session.isoformat()}")
            for guard in state.hard_guards:
                print(f"hard guard: {guard.kind.value}/{guard.guard_id}: {guard.reason}")
            return
        if args.drift_command == "freeze":
            envelope = _load_drift_envelope(args.envelope)
            state = registry.freeze_envelope(envelope)
            print(f"frozen envelope: {state.envelope.envelope_id if state.envelope else '-'}")
            return
        if args.drift_command == "activate":
            state = registry.bind_activation(
                strategy_id=args.strategy_id,
                envelope_id=args.envelope_id,
                activation_event_id=args.activation_event_id,
                occurred_at=args.timestamp or datetime.now(UTC),
            )
            print(f"drift activation bound: {state.activation_event_id}")
            return
        if args.drift_command == "observe":
            state = registry.read()
            if state.envelope is None:
                raise ValueError("observe requires a frozen envelope")
            metrics = tuple(_parse_drift_metric_observation(item) for item in args.metric)
            guards = tuple(_parse_drift_guard(item) for item in args.guard)
            metric_kinds = {state.envelope.metric(item.metric_id).kind for item in metrics}
            source_identities = list(args.source_identity)
            shadow_required = bool(
                metric_kinds & {DriftMetricKind.PERFORMANCE, DriftMetricKind.SIGNAL}
            )
            if shadow_required and not args.shadow_evidence_event_id:
                raise ValueError(
                    "performance and signal observations require --shadow-evidence-event-id"
                )
            completed_shadow_trades = 0
            if args.shadow_evidence_event_id:
                completed_shadow_trades = verified_shadow_trade_total(
                    state.envelope,
                    qualification_state=QualificationRegistry(args.qualification_path).read(),
                    evidence_event_id=args.shadow_evidence_event_id,
                    session=args.session,
                )
                source_identities.append(args.shadow_evidence_event_id)
            ledger_required = bool(
                metric_kinds
                & {
                    DriftMetricKind.EXECUTION,
                    DriftMetricKind.PORTFOLIO,
                    DriftMetricKind.UTILIZATION,
                    DriftMetricKind.CONCENTRATION,
                }
            ) or any(
                guard.kind
                in {
                    HardGuardKind.LEDGER,
                    HardGuardKind.RECONCILIATION,
                    HardGuardKind.EXECUTION,
                }
                for guard in guards
            )
            if ledger_required:
                replay = ManualLedgerStore(args.ledger_path).verify()
                source_identities.append(f"ledger-accounting:{replay.accounting_hash}")
            observation = DriftObservation.create(
                strategy_id=state.envelope.strategy_id,
                envelope_id=state.envelope.envelope_id,
                definition_fingerprint=state.envelope.definition_fingerprint,
                session=args.session,
                observed_at=args.observed_at or datetime.now(UTC),
                metrics=metrics,
                hard_guards=guards,
                source_identities=tuple(source_identities),
                completed_shadow_trades_total=completed_shadow_trades,
            )
            state = registry.record_observation(observation)
            print(f"observation recorded: {observation.observation_id}; state={state.state.value}")
            return
        if args.drift_command == "checkpoint":
            checkpoint = registry.record_checkpoint(
                ordinal=args.ordinal,
                session=args.session,
                evaluated_at=args.timestamp,
            )
            print(f"checkpoint {checkpoint.ordinal}: {checkpoint.state.value}")
            return
        if args.drift_command == "clean-check":
            state = registry.record_clean_check(
                session=args.session,
                evidence_identity=args.evidence_identity,
                occurred_at=args.timestamp or datetime.now(UTC),
            )
            print(f"clean check recorded: {state.state.value}")
            return
        if args.drift_command == "recover":
            decision = registry.recover(
                current_session=args.current_session,
                occurred_at=args.timestamp,
            )
            print(
                f"recovered: {decision.recovery_kind}; "
                f"sessions={decision.sessions_after_pause}; "
                f"trades={decision.completed_shadow_trades_after_pause}"
            )
            return
        raise ValueError(f"unsupported drift command: {args.drift_command}")
    except (OSError, TypeError, ValueError, LiveDriftRegistryError) as exc:
        print(f"drift error: {exc}")
        raise SystemExit(1) from exc


def _load_drift_envelope(path: Path) -> object:
    """Decode a canonical envelope manifest supplied by an operator, without network access."""
    from trading.core.live_drift import (
        DriftMetricExpectation,
        DriftMetricKind,
        PredictiveDriftEnvelope,
    )

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, Mapping) and isinstance(raw.get("envelope"), Mapping):
        raw = raw["envelope"]
    if not isinstance(raw, Mapping):
        raise ValueError("drift envelope manifest must contain an object")
    metrics = tuple(
        DriftMetricExpectation.create(
            metric_id=str(item["metric_id"]),
            kind=DriftMetricKind(str(item.get("kind", "performance"))),
            direction=str(item["direction"]),
            watch_boundary=str(item["watch_boundary"]),
            pause_boundary=str(item["pause_boundary"]),
            minimum_observations=int(item["minimum_observations"]),
            window_sessions=int(item["window_sessions"]),
            unit=str(item.get("unit", "ratio")),
        )
        for item in raw.get("metrics", ())
        if isinstance(item, Mapping)
    )
    return PredictiveDriftEnvelope.create(
        strategy_id=str(raw["strategy_id"]),
        definition_fingerprint=str(raw["definition_fingerprint"]),
        source_identities=tuple(str(value) for value in raw["source_identities"]),
        metrics=metrics,
        activation_anchor=date.fromisoformat(str(raw["activation_anchor"])),
        checkpoint_interval_sessions=int(raw["checkpoint_interval_sessions"]),
        bootstrap_seed=int(raw["bootstrap_seed"]),
        bootstrap_repetitions=int(raw["bootstrap_repetitions"]),
        bootstrap_block_sessions=int(raw["bootstrap_block_sessions"]),
        frozen_at=iso_datetime(str(raw["frozen_at"])),
        hard_guard_kinds=tuple(str(value) for value in raw.get("hard_guard_kinds", ())),
    )


def _parse_drift_metric_observation(item: str) -> object:
    from trading.core.live_drift import DriftMetricObservation

    metric_id, separator, remainder = item.partition("=")
    value_text, separator2, sample_text = remainder.partition(":")
    if not separator or not separator2:
        raise ValueError("metric must use METRIC_ID=DECIMAL:SAMPLE_COUNT")
    return DriftMetricObservation.create(
        metric_id=metric_id,
        value=value_text,
        sample_count=int(sample_text),
    )


def _parse_drift_guard(item: str) -> object:
    from trading.core.live_drift import HardGuardKind, HardGuardObservation

    parts = item.split(":", 4)
    if len(parts) != 5:
        raise ValueError("guard must use KIND:GUARD_ID:ACTIVE:EVIDENCE_ID:REASON")
    kind, guard_id, active, evidence_identity, reason = parts
    if active.lower() not in {"true", "false"}:
        raise ValueError("guard active value must be true or false")
    return HardGuardObservation.create(
        kind=HardGuardKind(kind),
        guard_id=guard_id,
        active=active.lower() == "true",
        evidence_identity=evidence_identity,
        reason=reason,
    )


def cmd_ledger(args: argparse.Namespace) -> None:
    """Manage the local dry-run manual execution ledger."""
    try:
        path = getattr(args, "path", None) or DEFAULT_MANUAL_LEDGER_PATH
        if args.ledger_command == "init":
            if args.managed_capital is None or not args.universe:
                raise ValueError("ledger init requires --managed-capital and --universe")
            initialization = LedgerInitialization.create(
                managed_capital=args.managed_capital,
                universe=args.universe,
                initialized_at=args.timestamp or datetime.now(UTC),
                allocation_epoch=args.allocation_epoch,
                currency=args.currency,
            )
            replay = ManualLedgerStore(path).initialize(initialization)
            print(
                f"ledger initialized: {path} (head={replay.head_hash}, "
                f"managed capital={replay.managed_capital})"
            )
            return

        store = ManualLedgerStore(path)
        if args.ledger_command == "verify":
            replay = store.verify()
            print(f"ledger valid: {path}")
            print(f"  head: {replay.head_hash}")
            print(f"  cash: {replay.cash}")
            print(f"  positions: {len(replay.positions)}")
            print(f"  proposals: {len(replay.proposals)}")
            return
        if args.ledger_command == "allocate":
            if not args.allocation_epoch or not args.sleeve_capital:
                raise ValueError("ledger allocate requires --allocation-epoch and --sleeve-capital")
            sleeve_capital: dict[str, str] = {}
            for assignment in args.sleeve_capital or ():
                symbol, separator, amount = assignment.partition("=")
                symbol = symbol.strip().upper()
                if separator != "=" or not symbol or not amount.strip():
                    raise ValueError("sleeve capital must use SYMBOL=DECIMAL")
                if symbol in sleeve_capital:
                    raise ValueError(f"duplicate sleeve capital assignment: {symbol}")
                sleeve_capital[symbol] = amount.strip()
            replay = store.start_allocation_epoch(
                args.allocation_epoch,
                sleeve_capital=sleeve_capital,
                reserve_cash=args.reserve_cash,
                occurred_at=args.timestamp or datetime.now(UTC),
            )
            print(
                f"allocation epoch started: {replay.allocation_epoch} "
                f"(universe={','.join(replay.universe)})"
            )
            return
        if args.ledger_command == "record":
            event = _record_ledger_event(store, args)
            print(f"recorded {event.event_type}: {event.event_id}")
            return
        if args.ledger_command == "reconcile":
            if args.broker_export is None:
                raise ValueError("ledger reconcile requires --broker-export")
            report = store.reconcile(args.broker_export, args.report)
            status = "ok" if report.ok else "failed"
            print(f"reconciliation {status}: {args.report}")
            for error in report.errors:
                print(f"  error: {error}")
            if not report.ok:
                raise SystemExit(1)
            return
        if args.ledger_command == "export":
            if args.destination is None:
                raise ValueError("ledger export requires a destination")
            destination = store.export(args.destination)
            print(f"ledger exported: {destination}")
            return
        if args.ledger_command == "import":
            if args.source is None:
                raise ValueError("ledger import requires a source")
            replay = store.import_ledger(args.source)
            print(f"ledger imported: {args.source} -> {path} (head={replay.head_hash})")
            return
        raise ValueError(f"unsupported ledger command: {args.ledger_command}")
    except SystemExit:
        raise
    except (LedgerError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ledger error: {exc}")
        raise SystemExit(1) from exc


def _record_submission_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    if args.proposal_terms_json is None:
        raise ValueError("submission requires --proposal-terms-json")
    payload = json.loads(args.proposal_terms_json)
    if not isinstance(payload, dict):
        raise ValueError("--proposal-terms-json must contain an object")
    proposal = ProposalTerms.from_payload(payload)
    if args.proposal_id and args.proposal_id != proposal.proposal_id:
        raise ValueError("--proposal-id does not match proposal terms")
    return store.record_submission(proposal, occurred_at=args.timestamp, event_id=args.event_id)


def _record_fill_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    required = {
        "proposal_id": args.proposal_id,
        "sleeve_id": args.sleeve_id,
        "instrument": args.instrument,
        "side": args.side,
        "quantity": args.quantity,
        "price": args.price,
    }
    if any(value is None for value in required.values()):
        raise ValueError("fill requires proposal, sleeve, instrument, side, quantity, and price")
    return store.record_fill(
        proposal_id=args.proposal_id,
        sleeve_id=args.sleeve_id,
        instrument=args.instrument,
        side=args.side,
        quantity=args.quantity,
        price=args.price,
        fee=args.fee,
        event_type=args.event_type,
        occurred_at=args.timestamp,
        event_id=args.event_id,
        external_id=args.external_id,
    )


def _record_cancellation_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    if args.proposal_id is None:
        raise ValueError("cancellation requires --proposal-id")
    return store.record_cancellation(
        args.proposal_id,
        occurred_at=args.timestamp,
        event_id=args.event_id,
    )


def _record_cash_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    if args.amount is None:
        raise ValueError(f"{args.event_type} requires --amount")
    return store.record_cash_event(
        args.event_type,
        args.amount,
        sleeve_id=args.sleeve_id or "",
        occurred_at=args.timestamp,
        event_id=args.event_id,
        external_id=args.external_id,
    )


def _record_correction_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    if args.correction_of is None or args.changes_json is None:
        raise ValueError("correction requires --correction-of and --changes-json")
    changes = json.loads(args.changes_json)
    if not isinstance(changes, dict):
        raise ValueError("--changes-json must contain an object")
    return store.record_correction(
        args.correction_of,
        changes,
        occurred_at=args.timestamp,
        event_id=args.event_id,
    )


def _record_manual_adjustment_event(
    store: ManualLedgerStore,
    args: argparse.Namespace,
) -> LedgerEvent:
    return store.record_manual_adjustment(
        classification=args.classification or "unrelated_manual",
        sleeve_id=args.sleeve_id or "",
        instrument=args.instrument or "",
        side=args.side or "",
        quantity=args.quantity,
        price=args.price,
        amount=args.amount,
        position_id=args.position_id or "",
        occurred_at=args.timestamp,
        event_id=args.event_id,
        external_id=args.external_id,
    )


_LEDGER_RECORD_HANDLERS = {
    "submission": _record_submission_event,
    **{event_type: _record_fill_event for event_type in FILL_EVENT_TYPES},
    "cancellation": _record_cancellation_event,
    **{event_type: _record_cash_event for event_type in CASH_EVENT_TYPES},
    "correction": _record_correction_event,
    "manual_adjustment": _record_manual_adjustment_event,
}


def _record_ledger_event(store: ManualLedgerStore, args: argparse.Namespace) -> LedgerEvent:
    event_type = args.event_type
    if event_type is None or event_type not in RECORDABLE_EVENT_TYPES:
        raise ValueError("ledger record requires a supported --event-type")
    return _LEDGER_RECORD_HANDLERS[event_type](store, args)


def cmd_data_status(args: argparse.Namespace) -> None:
    """Inspect one active cache series without network access or writes."""
    service = create_default_market_data_service()
    series = MarketDataSeries.yahoo_adjusted_daily(args.symbol)
    inspection = service.status(series)
    print(f"{series.symbol}: {inspection.state}")
    if inspection.metadata is not None:
        metadata = inspection.metadata
        print(f"  data cutoff: {metadata.data_cutoff.isoformat()}")
        print(f"  last incremental refresh: {metadata.last_incremental_refresh or '-'}")
        print(f"  last complete refresh: {metadata.last_complete_refresh or '-'}")
        print(f"  checksum: {metadata.checksum}")
    for error in inspection.errors:
        print(f"  error: {error}")


def cmd_data_refresh(args: argparse.Namespace) -> None:
    """Explicitly refresh and publish one validated cache series."""
    if args.full and args.start is not None:
        raise SystemExit(
            "--start cannot be used with --full; full refresh always downloads complete history"
        )
    service = create_default_market_data_service()
    series = MarketDataSeries.yahoo_adjusted_daily(args.symbol)
    mode = "full" if args.full else "incremental"
    frame = service.refresh(series, mode=mode, start=args.start, end=args.end)
    cutoff = frame.index[-1].strftime("%Y-%m-%d")
    print(f"{series.symbol}: {mode} refresh published {len(frame)} rows through {cutoff}")


def cmd_data_snapshot(args: argparse.Namespace) -> None:
    """Fully refresh declared series and publish one immutable snapshot manifest."""
    if args.experiment is not None:
        raise SystemExit(LEGACY_EXPERIMENT_RETIREMENT_MESSAGE)
    manifest_path = args.manifest
    if manifest_path is None:
        raise SystemExit("data-only snapshot requires --manifest PATH")
    service = create_default_market_data_service()
    store = create_default_research_data_store()
    primary = MarketDataSeries.yahoo_adjusted_daily(args.symbol)
    auxiliary = [MarketDataSeries.yahoo_adjusted_daily(symbol) for symbol in args.aux]
    requirements = [
        MarketDataRequirement(
            primary,
            args.history_start,
            role="primary",
        )
    ]
    requirements.extend(
        MarketDataRequirement(
            series,
            args.history_start,
            role="auxiliary",
            availability_policy=AvailabilityPolicy(
                publication_lag_sessions=args.aux_publication_lag,
                max_observation_lag_sessions=args.aux_max_observation_lag,
                publication_time_known=args.aux_publication_time_known,
            ),
        )
        for series in auxiliary
    )
    for requirement in requirements:
        refresh_kwargs = {
            "mode": "full",
            "start": None,
            "end": args.decision,
        }
        if requirement.coverage_policy != MarketDataCoveragePolicy.xnys():
            refresh_kwargs["coverage_policy"] = requirement.coverage_policy
        service.refresh(requirement.series, **refresh_kwargs)
    manifest = store.create_snapshot(
        service.cache,
        requirements,
        SignalDecisionTime.for_primary_session(args.decision),
    )
    path = store.write_manifest(manifest, manifest_path)
    print(f"snapshot {manifest.snapshot_id} published to {path}")


def cmd_data_verify(args: argparse.Namespace) -> None:
    """Verify a manifest and every immutable blob without network or writes."""
    snapshot = create_default_research_data_store().load_snapshot(args.manifest)
    definition = snapshot.manifest.definition
    print(f"snapshot {snapshot.manifest.snapshot_id}: valid")
    print(f"  series: {len(snapshot.manifest.data)}")
    print(f"  definition: {definition.fingerprint if definition else '-'}")


def cmd_data_export(args: argparse.Namespace) -> None:
    """Export a verified portable snapshot bundle."""
    store = create_default_research_data_store()
    manifest = store.load_manifest(args.manifest)
    result = None
    if args.result is not None:
        loaded = json.loads(args.result.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SystemExit("--result must contain a JSON object")
        result = loaded
    destination = store.export_bundle(manifest, args.destination, result=result)
    print(f"snapshot bundle exported to {destination}")


def cmd_data_import(args: argparse.Namespace) -> None:
    """Verify and import a portable snapshot bundle."""
    imported = create_default_research_data_store().import_bundle(
        args.bundle,
        manifest_path=args.manifest,
    )
    print(f"snapshot {imported.manifest.snapshot_id} imported to {imported.manifest_path}")


def cmd_data_gc(args: argparse.Namespace) -> None:
    """Plan or explicitly apply reference-aware immutable-blob garbage collection."""
    manifest_roots = tuple(dict.fromkeys((Path("results"), *(args.manifest_roots or ()))))
    report = create_default_research_data_store().collect_garbage(
        manifest_roots=manifest_roots,
        grace_period=timedelta(days=args.grace_days),
        apply=args.apply,
    )
    action = "deleted" if args.apply else "candidate"
    print(f"GC {action} blobs: {len(report.deleted if args.apply else report.candidates)}")
    for path in report.deleted if args.apply else report.candidates:
        print(f"  {path}")
    print(f"protected referenced blobs: {len(report.protected)}")


def positive_int(value: str) -> int:
    """Parse a strictly positive integer for argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def nonnegative_int(value: str) -> int:
    """Parse a non-negative integer for qualification dependency boundaries."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def iso_date(value: str) -> date:
    """Parse a strict ISO calendar date for argparse."""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a date in YYYY-MM-DD format") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("must be a date in YYYY-MM-DD format")
    return parsed


def iso_datetime(value: str) -> datetime:
    """Parse an aware ISO-8601 timestamp for ledger event ordering."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an aware ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("must include a timezone")
    return parsed.astimezone(UTC)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser independently from command dispatch."""
    parser = argparse.ArgumentParser(
        description="量化交易實驗框架 (Quantitative Trading Experiment Framework)",
        prog="trading",
    )
    sub = parser.add_subparsers(dest="command")

    legacy_commands.register_namespace(sub, iso_date=iso_date, positive_int=positive_int)

    # followup
    followup_p = sub.add_parser(
        "followup", help="產生跟單訊號報告 (Generate Firstrade trading signals)"
    )
    followup_p.add_argument("--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    followup_p.add_argument("--reconciliation-path", type=Path, default=DEFAULT_RECONCILIATION_PATH)
    followup_p.add_argument(
        "--lifecycle-path",
        type=Path,
        default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH,
    )
    followup_p.add_argument(
        "--drift-path",
        type=Path,
        default=DEFAULT_LIVE_DRIFT_PATH,
        help="Private per-strategy Phase 8 drift registry directory",
    )

    followup_state_p = sub.add_parser(
        "followup-state",
        help="Manage controlled followup cutover lifecycle",
    )
    followup_state_sub = followup_state_p.add_subparsers(
        dest="followup_state_command",
        required=True,
    )
    followup_state_init_p = followup_state_sub.add_parser(
        "init",
        help="Initialize Legacy Active state from a reconciled ledger",
    )
    followup_state_init_p.add_argument("--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH)
    followup_state_init_p.add_argument(
        "--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH
    )
    followup_state_init_p.add_argument(
        "--reconciliation-path", type=Path, default=DEFAULT_RECONCILIATION_PATH
    )
    followup_state_init_p.add_argument("--timestamp", type=iso_datetime)
    followup_state_init_p.add_argument(
        "--position-owner",
        action="append",
        default=[],
        help="User-verified owner for an unlinked open position: TICKER=EXPERIMENT",
    )
    followup_state_status_p = followup_state_sub.add_parser(
        "status",
        help="Read verified strategy lifecycle state",
    )
    followup_state_status_p.add_argument(
        "--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH
    )
    for mode in ("pause", "resume"):
        mode_parser = followup_state_sub.add_parser(
            mode,
            help=f"{mode.title()} global new-entry authorization",
        )
        mode_parser.add_argument("--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH)
        mode_parser.add_argument("--reason", required=True)
        mode_parser.add_argument("--timestamp", type=iso_datetime)
    followup_state_activate_p = followup_state_sub.add_parser(
        "activate",
        help="Activate only after verified parity and prospective qualification",
    )
    followup_state_activate_p.add_argument(
        "--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH
    )
    followup_state_activate_p.add_argument(
        "--qualification-path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    followup_state_activate_p.add_argument("--ticker", required=True)
    followup_state_activate_p.add_argument("--experiment", required=True)
    followup_state_activate_p.add_argument("--shadow-id", required=True)
    followup_state_activate_p.add_argument("--qualification-event-id", required=True)
    followup_state_activate_p.add_argument("--result-fingerprint", required=True)
    followup_state_activate_p.add_argument("--parity-digest", required=True)
    followup_state_activate_p.add_argument(
        "--drift-envelope-id",
        help="Frozen predictive drift envelope identity required for activation",
    )
    followup_state_activate_p.add_argument(
        "--drift-path",
        type=Path,
        default=Path("state/live-drift.json"),
    )
    followup_state_activate_p.add_argument("--reason", required=True)
    followup_state_activate_p.add_argument("--timestamp", type=iso_datetime)
    followup_state_shadow_p = followup_state_sub.add_parser(
        "shadow",
        help="Register Shadow only from verified parity and Historical Screen evidence",
    )
    followup_state_shadow_p.add_argument(
        "--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH
    )
    followup_state_shadow_p.add_argument(
        "--qualification-path", type=Path, default=DEFAULT_QUALIFICATION_REGISTRY_PATH
    )
    followup_state_shadow_p.add_argument("--ticker", required=True)
    followup_state_shadow_p.add_argument("--experiment", required=True)
    followup_state_shadow_p.add_argument("--shadow-id", required=True)
    followup_state_shadow_p.add_argument("--registration-event-id", required=True)
    followup_state_shadow_p.add_argument("--historical-screen-event-id", required=True)
    followup_state_shadow_p.add_argument("--result-fingerprint", required=True)
    followup_state_shadow_p.add_argument("--parity-digest", required=True)
    followup_state_shadow_p.add_argument("--reason", required=True)
    followup_state_shadow_p.add_argument("--timestamp", type=iso_datetime)
    for operation in ("retire", "complete-retirement"):
        retirement_parser = followup_state_sub.add_parser(
            operation,
            help="Start retirement or complete it after verified flat ledger state",
        )
        retirement_parser.add_argument("--path", type=Path, default=DEFAULT_FOLLOWUP_LIFECYCLE_PATH)
        retirement_parser.add_argument(
            "--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH
        )
        retirement_parser.add_argument(
            "--reconciliation-path", type=Path, default=DEFAULT_RECONCILIATION_PATH
        )
        retirement_parser.add_argument("--ticker", required=True)
        retirement_parser.add_argument("--experiment", required=True)
        retirement_parser.add_argument("--reason", required=True)
        retirement_parser.add_argument("--timestamp", type=iso_datetime)

    # live drift and recovery (private, dry-run evidence only)
    drift_p = sub.add_parser(
        "drift",
        help="Inspect and append private Phase 8 drift evidence; never contacts a broker",
    )
    drift_sub = drift_p.add_subparsers(dest="drift_command", required=True)
    drift_status_p = drift_sub.add_parser("status", help="Read verified drift state")
    drift_status_p.add_argument("--path", type=Path, default=Path("state/live-drift.json"))
    drift_freeze_p = drift_sub.add_parser("freeze", help="Freeze a predictive envelope manifest")
    drift_freeze_p.add_argument("--path", type=Path, required=True)
    drift_freeze_p.add_argument("--envelope", type=Path, required=True)
    drift_activate_p = drift_sub.add_parser(
        "activate", help="Bind an envelope to Phase 7 activation"
    )
    drift_activate_p.add_argument("--path", type=Path, required=True)
    drift_activate_p.add_argument("--strategy-id", required=True)
    drift_activate_p.add_argument("--envelope-id", required=True)
    drift_activate_p.add_argument("--activation-event-id", required=True)
    drift_activate_p.add_argument("--timestamp", type=iso_datetime)
    drift_observe_p = drift_sub.add_parser(
        "observe", help="Append one completed-session observation"
    )
    drift_observe_p.add_argument("--path", type=Path, required=True)
    drift_observe_p.add_argument("--session", type=iso_date, required=True)
    drift_observe_p.add_argument("--observed-at", type=iso_datetime)
    drift_observe_p.add_argument("--metric", action="append", default=[], required=True)
    drift_observe_p.add_argument("--guard", action="append", default=[])
    drift_observe_p.add_argument("--source-identity", action="append", default=[])
    drift_observe_p.add_argument("--shadow-evidence-event-id")
    drift_observe_p.add_argument(
        "--qualification-path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    drift_observe_p.add_argument("--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    drift_checkpoint_p = drift_sub.add_parser("checkpoint", help="Evaluate a scheduled checkpoint")
    drift_checkpoint_p.add_argument("--path", type=Path, required=True)
    drift_checkpoint_p.add_argument("--ordinal", type=positive_int, required=True)
    drift_checkpoint_p.add_argument("--session", type=iso_date, required=True)
    drift_checkpoint_p.add_argument("--timestamp", type=iso_datetime)
    drift_clean_p = drift_sub.add_parser(
        "clean-check", help="Record a verified clean integrity check"
    )
    drift_clean_p.add_argument("--path", type=Path, required=True)
    drift_clean_p.add_argument("--session", type=iso_date, required=True)
    drift_clean_p.add_argument("--evidence-identity", required=True)
    drift_clean_p.add_argument("--timestamp", type=iso_datetime)
    drift_clean_p.add_argument("--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    drift_clean_p.add_argument(
        "--reconciliation-path", type=Path, default=DEFAULT_RECONCILIATION_PATH
    )
    drift_recover_p = drift_sub.add_parser("recover", help="Evaluate a fail-closed recovery gate")
    drift_recover_p.add_argument("--path", type=Path, required=True)
    drift_recover_p.add_argument("--current-session", type=iso_date, required=True)
    drift_recover_p.add_argument("--timestamp", type=iso_datetime)
    drift_recover_p.add_argument("--ledger-path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    drift_recover_p.add_argument(
        "--reconciliation-path", type=Path, default=DEFAULT_RECONCILIATION_PATH
    )

    qualification_p = sub.add_parser(
        "qualification",
        help="Historical qualification and Shadow lifecycle operations",
    )
    qualification_sub = qualification_p.add_subparsers(
        dest="qualification_command",
        required=True,
    )
    qualification_status_p = qualification_sub.add_parser(
        "status",
        help="Show persisted qualification lifecycle",
    )
    qualification_status_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_evidence_p = qualification_sub.add_parser(
        "evidence-snapshot",
        help="Publish a verified content-addressed qualification registry snapshot",
    )
    qualification_evidence_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_evidence_p.add_argument(
        "--output-root",
        type=Path,
        default=qualification_evidence_directory(),
    )
    qualification_evidence_p.add_argument(
        "--source-registry-identity",
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH.as_posix(),
        help="Preregistered repository-relative identity of the captured registry",
    )
    qualification_shared_p = qualification_sub.add_parser(
        "shared-state",
        help="Inspect or migrate the Git-common shared qualification authority",
    )
    qualification_shared_sub = qualification_shared_p.add_subparsers(
        dest="shared_state_command",
        required=True,
    )
    qualification_shared_status_p = qualification_shared_sub.add_parser(
        "status",
        help="Replay the complete shared catalog without changing it",
    )
    qualification_shared_status_p.add_argument(
        "--repository-root",
        type=Path,
        default=Path("."),
    )
    qualification_shared_evidence_p = qualification_shared_sub.add_parser(
        "evidence-snapshot",
        help="Publish a provider-free snapshot of the catalog, every shard, and active chain",
    )
    qualification_shared_evidence_p.add_argument(
        "--repository-root",
        type=Path,
        default=Path("."),
    )
    qualification_shared_evidence_p.add_argument(
        "--output-root",
        type=Path,
        default=qualification_evidence_directory(),
    )
    qualification_shared_preview_p = qualification_shared_sub.add_parser(
        "migration-preview",
        help="Derive the exact complete-inventory migration decision without writing",
    )
    qualification_shared_apply_p = qualification_shared_sub.add_parser(
        "migration-apply",
        help="Publish an exact separately approved migration under an effective workflow",
    )
    qualification_shared_close_p = qualification_shared_sub.add_parser(
        "close-plan",
        help="Append one separately approved imported-plan administrative terminal",
    )
    for migration_parser in (qualification_shared_preview_p, qualification_shared_apply_p):
        migration_parser.add_argument("--request", type=Path, required=True)
        migration_parser.add_argument("--workflow", type=Path, required=True)
        migration_parser.add_argument(
            "--repository-root",
            type=Path,
            default=Path("."),
        )
    qualification_shared_apply_p.add_argument(
        "--approved-decision-sha256",
        required=True,
        help="Exact digest emitted by migration-preview and separately approved by the human",
    )
    qualification_shared_close_p.add_argument("--plan-id", required=True)
    qualification_shared_close_p.add_argument(
        "--disposition",
        choices=("cancelled", "close-invalidated"),
        required=True,
    )
    qualification_shared_close_p.add_argument("--workflow", type=Path, required=True)
    qualification_shared_close_p.add_argument(
        "--impact-change",
        type=Path,
        required=True,
        help="Accepted change directory containing exact IMPACT.md and DECISION.md",
    )
    qualification_shared_close_p.add_argument("--approved-by", required=True)
    qualification_shared_close_p.add_argument("--reason", required=True)
    qualification_shared_close_p.add_argument(
        "--repository-root",
        type=Path,
        default=Path("."),
    )
    qualification_plan_p = qualification_sub.add_parser(
        "plan",
        help="Manage preregistered forward qualification plans",
    )
    qualification_plan_sub = qualification_plan_p.add_subparsers(
        dest="plan_command",
        required=True,
    )
    qualification_plan_register_p = qualification_plan_sub.add_parser(
        "register",
        help="Freeze a future-only selection epoch and Historical Screen plan",
    )
    qualification_plan_study_p = qualification_plan_sub.add_parser(
        "register-study",
        help="Compile or register a complete plan derived from one exact frozen study",
    )
    qualification_plan_abandon_p = qualification_plan_sub.add_parser(
        "abandon",
        help="Close an unscreened plan owned by an exactly bound cancelled study",
    )
    qualification_plan_abandon_p.add_argument("--plan-id", required=True)
    qualification_plan_abandon_p.add_argument(
        "--workflow",
        type=Path,
        required=True,
        help="Exact active workflow version granting plan-abandonment capability",
    )
    qualification_plan_abandon_p.add_argument("--approved-by", required=True)
    qualification_plan_abandon_p.add_argument("--reason", required=True)
    qualification_plan_abandon_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_plan_study_p.add_argument("--study", type=Path, required=True)
    qualification_plan_study_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_plan_study_p.add_argument(
        "--trial-registry-path",
        type=Path,
        default=trial_registry_path(),
    )
    qualification_plan_study_p.add_argument("--dry-run", action="store_true")
    qualification_plan_study_p.add_argument(
        "--approved-by",
        help="Separate current human approval; required for registry mutation",
    )
    qualification_plan_study_p.add_argument(
        "--contamination-declaration",
        help="Current human provenance/contamination declaration; required for mutation",
    )
    qualification_plan_register_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_plan_register_p.add_argument(
        "--trial-registry-path",
        type=Path,
        default=trial_registry_path(),
    )
    qualification_identity = qualification_plan_register_p.add_mutually_exclusive_group(
        required=True
    )
    qualification_identity.add_argument(
        "--experiment",
        help="Retired legacy qualification input; always fails closed",
    )
    qualification_identity.add_argument(
        "--research",
        help="Workflow-native family/trial research-definition identity",
    )
    qualification_plan_register_p.add_argument(
        "--family-research",
        action="append",
        help=(
            "Outcome-free family/trial source identity; repeat to freeze the complete family "
            "in one current-time registration"
        ),
    )
    qualification_plan_register_p.add_argument(
        "--family-source-sha",
        action="append",
        help="Frozen IDENTITY=SHA256 source bytes; repeat for every --family-research identity",
    )
    qualification_plan_register_p.add_argument(
        "--family-trial-budget",
        type=positive_int,
        help="Frozen maximum trial count; must equal the complete prepared family",
    )
    qualification_plan_register_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Compile and print the exact plan without changing trial or qualification registries",
    )
    qualification_plan_register_p.add_argument(
        "--workflow",
        type=Path,
        help="Exact released workflow path; required with --research",
    )
    qualification_plan_register_p.add_argument("--family-baseline-trial-id", required=True)
    qualification_plan_register_p.add_argument(
        "--evaluation-years",
        type=int,
        nargs="+",
        required=True,
    )
    qualification_plan_register_p.add_argument(
        "--development-years",
        type=int,
        nargs="+",
        help=(
            "Explicit Development-context years for retrospective role-calendar registration; "
            "requires both warmup bounds"
        ),
    )
    qualification_plan_register_p.add_argument(
        "--warmup-start",
        type=iso_date,
        help="First warmup-only session bound for an explicit retrospective role calendar",
    )
    qualification_plan_register_p.add_argument(
        "--warmup-end",
        type=iso_date,
        help="Last warmup-only session bound for an explicit retrospective role calendar",
    )
    qualification_plan_register_p.add_argument(
        "--quarantine-years",
        type=int,
        nargs="*",
        help=(
            "Explicit whole-year quarantine inventory; pass the flag with no years to freeze "
            "an intentionally empty quarantine"
        ),
    )
    qualification_plan_register_p.add_argument(
        "--maximum-holding-sessions",
        type=nonnegative_int,
        required=True,
    )
    qualification_plan_register_p.add_argument(
        "--execution-lag-sessions",
        type=nonnegative_int,
        required=True,
    )
    qualification_plan_register_p.add_argument(
        "--dependency-sessions",
        type=nonnegative_int,
        required=True,
    )
    qualification_plan_register_p.add_argument(
        "--embargo-sessions",
        type=nonnegative_int,
        required=True,
    )
    qualification_plan_register_p.add_argument("--stress-drawdown-limit", default="0.20")
    qualification_plan_register_p.add_argument("--random-seed", type=int, required=True)
    qualification_plan_register_p.add_argument(
        "--random-samples",
        type=positive_int,
        default=1000,
    )
    qualification_plan_register_p.add_argument(
        "--bootstrap-repetitions",
        type=positive_int,
        default=1000,
    )
    qualification_plan_register_p.add_argument(
        "--bootstrap-block-sessions",
        type=positive_int,
        default=20,
    )
    qualification_plan_register_p.add_argument(
        "--evidence-role",
        choices=(
            "historical",
            "retrospective-confirmatory",
            "study-time-retrospective",
        ),
        default="historical",
    )
    qualification_plan_register_p.add_argument(
        "--evidence-classification",
        choices=("verified-clean", "known-contaminated", "provenance-unknown"),
    )
    qualification_plan_register_p.add_argument("--audit-justification")
    qualification_plan_register_p.add_argument("--trial-history-complete", action="store_true")
    qualification_screen_p = qualification_sub.add_parser(
        "screen",
        help="Run a completed preregistered Historical Screen",
    )
    qualification_screen_sub = qualification_screen_p.add_subparsers(
        dest="screen_command",
        required=True,
    )
    qualification_screen_run_p = qualification_screen_sub.add_parser(
        "run",
        help="Recompute a screen from exact formal trial snapshots",
    )
    qualification_screen_run_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_screen_run_p.add_argument(
        "--trial-registry-path",
        type=Path,
        default=trial_registry_path(),
    )
    qualification_screen_run_p.add_argument("--plan-id", required=True)
    qualification_screen_run_p.add_argument(
        "--workflow",
        type=Path,
        help="Exact released workflow path for workflow-native trial identities",
    )
    qualification_screen_run_p.add_argument(
        "--trial",
        action="append",
        required=True,
        help="IDENTITY=MANIFEST; repeat for every frozen family trial",
    )
    qualification_challenge_p = qualification_sub.add_parser(
        "challenge",
        help="Run independent provider-free fixed Evaluation challenges",
    )
    qualification_challenge_sub = qualification_challenge_p.add_subparsers(
        dest="challenge_command",
        required=True,
    )
    qualification_challenge_run_p = qualification_challenge_sub.add_parser(
        "run-study",
        help="Publish nine frozen challenge artifacts without screen or registry authority",
    )
    qualification_challenge_run_p.add_argument("--study", type=Path, required=True)
    qualification_challenge_run_p.add_argument("--plan-id", required=True)
    qualification_challenge_run_p.add_argument(
        "--trial",
        action="append",
        required=True,
        help="IDENTITY=MANIFEST; repeat for the exact frozen family",
    )
    qualification_challenge_run_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_challenge_run_p.add_argument(
        "--trial-registry-path",
        type=Path,
        default=trial_registry_path(),
    )
    qualification_challenge_run_p.add_argument("--output-root", type=Path)
    qualification_challenge_run_p.add_argument("--dry-run", action="store_true")
    qualification_replay_p = qualification_sub.add_parser(
        "replay",
        help="Run a non-actionable fixed-calendar retrospective execution replay",
    )
    qualification_replay_sub = qualification_replay_p.add_subparsers(
        dest="replay_command",
        required=True,
    )
    qualification_replay_run_p = qualification_replay_sub.add_parser(
        "run-study",
        help="Recompute and atomically publish the frozen 2025 historical replay",
    )
    qualification_replay_run_p.add_argument("--study", type=Path, required=True)
    qualification_replay_run_p.add_argument("--plan-id", required=True)
    qualification_replay_run_p.add_argument("--manifest", type=Path, required=True)
    qualification_replay_run_p.add_argument("--challenge-manifest", type=Path, required=True)
    qualification_replay_run_p.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_QUALIFICATION_REGISTRY_PATH,
    )
    qualification_replay_run_p.add_argument(
        "--trial-registry-path",
        type=Path,
        default=trial_registry_path(),
    )
    qualification_replay_run_p.add_argument("--output-root", type=Path)
    qualification_replay_run_p.add_argument("--dry-run", action="store_true")

    workflow_commands.register_parser(sub)

    # tracked executable policy authoring and release declarations
    policy_p = sub.add_parser(
        "policy",
        help="Validate and release versioned executable research policies",
    )
    policy_p.add_argument(
        "--root",
        type=Path,
        default=Path("policies"),
        help="Tracked policy registry root (default: policies)",
    )
    policy_sub = policy_p.add_subparsers(dest="policy_command", required=True)
    policy_validate_p = policy_sub.add_parser(
        "validate",
        help="Read-only validation of policy metadata and immutable evidence",
    )
    policy_validate_p.add_argument("path", type=Path, nargs="?")
    policy_validate_p.add_argument("--all", action="store_true")
    policy_sub.add_parser("sync", help="Regenerate the policy registry index")
    policy_version_p = policy_sub.add_parser(
        "version",
        help="Abandon a draft or retire an active policy version",
    )
    policy_version_sub = policy_version_p.add_subparsers(
        dest="policy_version_command",
        required=True,
    )
    policy_version_transition_p = policy_version_sub.add_parser(
        "transition",
        help="Apply an allowed terminal policy-version transition",
    )
    policy_version_transition_p.add_argument("path", type=Path)
    policy_version_transition_p.add_argument(
        "--to",
        dest="status",
        required=True,
        choices=("abandoned", "retired"),
    )
    policy_version_transition_p.add_argument("--approved-by")
    policy_release_p = policy_sub.add_parser(
        "release",
        help="Prepare an approved policy release declaration",
    )
    policy_release_p.add_argument("path", type=Path)
    policy_release_p.add_argument("--approved-by", required=True)

    research_commands.register_parser(sub, iso_date=iso_date)

    # freshness
    sub.add_parser("freshness", help="檢查知識新鮮度 (Check knowledge freshness)")

    # manual execution ledger
    ledger_p = sub.add_parser("ledger", help="管理本地手動成交 ledger (Manage manual ledger)")
    ledger_sub = ledger_p.add_subparsers(dest="ledger_command", required=True)
    ledger_init_p = ledger_sub.add_parser("init", help="Initialize managed capital and sleeves")
    ledger_init_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_init_p.add_argument("--managed-capital")
    ledger_init_p.add_argument("--universe", nargs="+")
    ledger_init_p.add_argument("--allocation-epoch", default="epoch-0001")
    ledger_init_p.add_argument("--currency", default="USD")
    ledger_init_p.add_argument("--timestamp", type=iso_datetime)
    ledger_verify_p = ledger_sub.add_parser("verify", help="Verify chain and replay invariants")
    ledger_verify_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_allocate_p = ledger_sub.add_parser(
        "allocate",
        help="Start an explicit flat-ledger allocation epoch",
    )
    ledger_allocate_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_allocate_p.add_argument("--allocation-epoch")
    ledger_allocate_p.add_argument("--sleeve-capital", nargs="+")
    ledger_allocate_p.add_argument("--reserve-cash", default="0")
    ledger_allocate_p.add_argument("--timestamp", type=iso_datetime)
    ledger_record_p = ledger_sub.add_parser("record", help="Append one ledger event")
    ledger_record_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_record_p.add_argument("--event-type", choices=sorted(RECORDABLE_EVENT_TYPES))
    ledger_record_p.add_argument("--event-id")
    ledger_record_p.add_argument("--timestamp", type=iso_datetime)
    ledger_record_p.add_argument("--proposal-id")
    ledger_record_p.add_argument("--proposal-terms-json")
    ledger_record_p.add_argument("--sleeve-id")
    ledger_record_p.add_argument("--instrument")
    ledger_record_p.add_argument("--side")
    ledger_record_p.add_argument("--quantity")
    ledger_record_p.add_argument("--price")
    ledger_record_p.add_argument("--amount")
    ledger_record_p.add_argument("--fee")
    ledger_record_p.add_argument("--position-id")
    ledger_record_p.add_argument("--classification")
    ledger_record_p.add_argument("--external-id")
    ledger_record_p.add_argument("--correction-of")
    ledger_record_p.add_argument("--changes-json")
    ledger_reconcile_p = ledger_sub.add_parser("reconcile", help="Compare with a broker CSV export")
    ledger_reconcile_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_reconcile_p.add_argument("--broker-export", type=Path)
    ledger_reconcile_p.add_argument("--report", type=Path, default=DEFAULT_RECONCILIATION_PATH)
    ledger_export_p = ledger_sub.add_parser("export", help="Export a verified ledger CSV")
    ledger_export_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_export_p.add_argument("destination", type=Path, nargs="?")
    ledger_import_p = ledger_sub.add_parser("import", help="Import a verified ledger CSV")
    ledger_import_p.add_argument("--path", type=Path, default=DEFAULT_MANUAL_LEDGER_PATH)
    ledger_import_p.add_argument("source", type=Path, nargs="?")

    # data
    data_p = sub.add_parser("data", help="Inspect or refresh the CSV market-data cache")
    data_sub = data_p.add_subparsers(dest="data_command", required=True)
    data_status_p = data_sub.add_parser("status", help="Read-only cache status")
    data_status_p.add_argument("symbol", help="Yahoo Finance ticker symbol")
    data_refresh_p = data_sub.add_parser("refresh", help="Explicit cache refresh")
    data_refresh_p.add_argument("symbol", help="Yahoo Finance ticker symbol")
    data_refresh_p.add_argument(
        "--full",
        action="store_true",
        help="Download full history and mark the series snapshot-eligible",
    )
    data_refresh_p.add_argument("--start", type=iso_date, help="Optional history start YYYY-MM-DD")
    data_refresh_p.add_argument("--end", type=iso_date, help="Optional inclusive cutoff YYYY-MM-DD")
    data_snapshot_p = data_sub.add_parser(
        "snapshot",
        help="Fully refresh declared series and publish an immutable data snapshot",
    )
    data_snapshot_p.add_argument("symbol", help="Primary Yahoo Finance ticker symbol")
    data_snapshot_p.add_argument(
        "--experiment",
        help="Retired legacy option (always fails closed)",
    )
    data_snapshot_p.add_argument(
        "--aux",
        action="append",
        default=[],
        help="Auxiliary Yahoo ticker; repeat for multiple declarations",
    )
    data_snapshot_p.add_argument(
        "--history-start",
        type=iso_date,
        required=True,
        help="Required history start YYYY-MM-DD",
    )
    data_snapshot_p.add_argument(
        "--decision",
        type=iso_date,
        required=True,
        help="Primary signal decision session YYYY-MM-DD",
    )
    data_snapshot_p.add_argument(
        "--manifest",
        type=Path,
        help="Required tracked destination for a data-only snapshot",
    )
    data_snapshot_p.add_argument("--aux-publication-lag", type=int, default=1)
    data_snapshot_p.add_argument("--aux-max-observation-lag", type=int, default=1)
    data_snapshot_p.add_argument(
        "--aux-publication-time-known",
        action="store_true",
        help="Declare exact daily publication timing as known",
    )
    data_verify_p = data_sub.add_parser("verify", help="Read-only snapshot verification")
    data_verify_p.add_argument("manifest", type=Path)
    data_export_p = data_sub.add_parser("export", help="Export a portable snapshot bundle")
    data_export_p.add_argument("manifest", type=Path)
    data_export_p.add_argument("destination", type=Path)
    data_export_p.add_argument("--result", type=Path, help="Optional result JSON to include")
    data_import_p = data_sub.add_parser("import", help="Import a portable snapshot bundle")
    data_import_p.add_argument("bundle", type=Path)
    data_import_p.add_argument("--manifest", type=Path, required=True)
    data_gc_p = data_sub.add_parser(
        "gc",
        help="Reference-aware immutable-blob GC; dry-run unless --apply is given",
    )
    data_gc_p.add_argument(
        "--manifest-root",
        action="append",
        dest="manifest_roots",
        type=Path,
        help="Retained-manifest root to scan recursively; defaults to results/",
    )
    data_gc_p.add_argument("--grace-days", type=positive_int, default=7)
    data_gc_p.add_argument("--apply", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI 主程式 (CLI main)"""
    parser = build_parser()

    args = parser.parse_args(argv)

    if args.command == "legacy":
        legacy_commands.dispatch(args)
    elif args.command == "followup":
        from trading.followup import run_followup

        if (
            args.ledger_path == DEFAULT_MANUAL_LEDGER_PATH
            and args.reconciliation_path == DEFAULT_RECONCILIATION_PATH
            and args.lifecycle_path == DEFAULT_FOLLOWUP_LIFECYCLE_PATH
            and args.drift_path == DEFAULT_LIVE_DRIFT_PATH
        ):
            run_followup()
        else:
            run_followup(
                ledger_path=args.ledger_path,
                reconciliation_path=args.reconciliation_path,
                lifecycle_path=args.lifecycle_path,
                drift_path=args.drift_path,
            )
    elif args.command == "followup-state":
        cmd_followup_state(args)
    elif args.command == "drift":
        cmd_drift(args)
    elif args.command == "qualification":
        cmd_qualification(args)
    elif args.command == "workflow":
        cmd_workflow(args)
    elif args.command == "policy":
        cmd_policy(args)
    elif args.command == "research":
        cmd_research(args)
    elif args.command == "freshness":
        from trading.knowledge_freshness import check_freshness

        check_freshness()
    elif args.command == "ledger":
        cmd_ledger(args)
    elif args.command == "data" and args.data_command == "status":
        cmd_data_status(args)
    elif args.command == "data" and args.data_command == "refresh":
        cmd_data_refresh(args)
    elif args.command == "data" and args.data_command == "snapshot":
        cmd_data_snapshot(args)
    elif args.command == "data" and args.data_command == "verify":
        cmd_data_verify(args)
    elif args.command == "data" and args.data_command == "export":
        cmd_data_export(args)
    elif args.command == "data" and args.data_command == "import":
        cmd_data_import(args)
    elif args.command == "data" and args.data_command == "gc":
        cmd_data_gc(args)
    else:
        # 無子命令時顯示幫助 (Show help when no subcommand)
        parser.print_help()
        sys.exit(0)

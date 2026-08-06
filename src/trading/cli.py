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

from trading.core.data_fetcher import create_default_market_data_service
from trading.core.definition_resolver import resolve_current_definition_fingerprint
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
from trading.core.proposals import ProposalTerms
from trading.core.results import compare_experiments, inspect_result, save_result
from trading.experiments import get_experiment, list_experiments
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.research_data import (
    ExperimentTrialDeclaration,
    ExperimentTrialRegistry,
    QualificationRegistry,
    ResearchDataStore,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunMode,
)

# 設定日誌格式 (Configure logging format)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

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


def cmd_list(args: argparse.Namespace) -> None:
    """列出所有已註冊的實驗 (List all registered experiments)"""
    experiments = list_experiments()
    print(f"\n  已註冊的實驗 (Registered experiments): {len(experiments)}")
    print(f"  {'=' * 40}")
    for name in experiments:
        strategy = get_experiment(name)
        config = strategy.create_config()
        eid = config.experiment_id or ""
        print(f"  - {eid:<10} {name:<30} {config.display_name}")
    print()


def cmd_run(args: argparse.Namespace) -> None:
    """執行實驗 (Run experiment(s))"""
    if args.all:
        names = list_experiments()
    elif args.experiment:
        names = [args.experiment]
    else:
        # 預設執行全部 (Default: run all)
        names = list_experiments()

    explicit_formal_manifest = args.offline or args.snapshot
    default_formal = explicit_formal_manifest is None and not args.ephemeral and not args.legacy
    if (explicit_formal_manifest is not None or default_formal) and len(names) != 1:
        raise SystemExit("formal snapshot execution requires exactly one experiment")

    for name in names:
        logger.info(f"執行實驗: {name} (Running experiment: {name})")
        strategy = get_experiment(name)
        formal_manifest = explicit_formal_manifest
        if formal_manifest is not None or default_formal:
            run_with_bundle = getattr(strategy, "run_with_bundle", None)
            capture_definition = getattr(strategy, "capture_research_definition", None)
            declare_trial = getattr(strategy, "declare_experiment_trial", None)
            if (
                not callable(run_with_bundle)
                or not callable(capture_definition)
                or not callable(declare_trial)
            ):
                if default_formal:
                    raise SystemExit(
                        "persisted runs require a snapshot-aware prepared manifest or "
                        "--snapshot MANIFEST; use --legacy only for unmigrated experiments"
                    )
                raise SystemExit(
                    f"{name} is not snapshot-aware; formal execution requires "
                    "run_with_bundle, capture_research_definition, and "
                    "declare_experiment_trial"
                )
            definition = capture_definition(create_default_research_definition_store())
            if not isinstance(definition, ResearchDefinitionSnapshot):
                raise SystemExit(
                    "capture_research_definition must return ResearchDefinitionSnapshot"
                )
            trial = declare_trial()
            if not isinstance(trial, ExperimentTrialDeclaration):
                raise SystemExit("declare_experiment_trial must return ExperimentTrialDeclaration")
            research_store = create_default_research_data_store()
            if default_formal:
                formal_manifest = research_store.latest_manifest_for_definition(
                    Path("results") / name,
                    definition.blob,
                )
            coordinator = ResearchRunCoordinator(
                store=research_store,
                results_root=Path("results"),
                experiment_family=trial.family,
                hypothesis=trial.hypothesis,
            )
            coordinator.execute(
                name,
                run_with_bundle,
                manifest_path=formal_manifest,
                current_definition=definition.blob,
                mode=RunMode.OFFLINE if args.offline is not None else RunMode.ONLINE,
            )
        elif args.ephemeral:
            result = strategy.run()
        elif args.legacy:
            result = strategy.run()
            # 儲存 legacy result (Save legacy result)
            save_result(name, result)

    if len(names) > 1:
        print("\n  所有實驗已完成 (All experiments completed)")


def cmd_compare(args: argparse.Namespace) -> None:
    """比較實驗結果 (Compare experiment results)"""
    compare_experiments(args.experiments)


def cmd_result_status(args: argparse.Namespace) -> None:
    """Show persisted-result validity without refreshing or executing anything."""
    from trading.core import results as result_module

    if args.all:
        names = (
            sorted(
                path.name
                for path in result_module.RESULTS_DIR.iterdir()
                if path.is_dir() and (path / "latest.json").exists()
            )
            if result_module.RESULTS_DIR.exists()
            else []
        )
    elif args.experiment:
        names = [args.experiment]
    else:
        raise SystemExit("result status requires an experiment name or --all")

    store = create_default_research_data_store()
    for name in names:
        record = inspect_result(
            name,
            results_dir=result_module.RESULTS_DIR,
            store=store,
            current_definition_fingerprint=resolve_current_definition_fingerprint(name),
        )
        if record is None:
            print(f"{name}: no latest result")
            continue
        print(f"{name}: {record.validity.status.value}")
        if record.result.payload:
            payload = record.result.payload
            print(f"  schema version: {payload.get('schema_version', 'legacy')}")
            print(f"  data cutoff: {payload.get('data_cutoff', '-')}")
            print(f"  definition fingerprint: {payload.get('definition_fingerprint', '-')}")
        for reason in record.validity.reasons:
            print(f"  reason: {reason}")


def cmd_result_registry_seed(args: argparse.Namespace) -> None:
    """Explicitly seed legacy experiment inventory entries in the trial registry."""
    from trading.core import results as result_module

    registry = ExperimentTrialRegistry(result_module.RESULTS_DIR / "trial_registry.json")
    identities = registry.seed_legacy(list_experiments())
    print(
        f"seeded {len(identities)} legacy trial entries; selection history is explicitly incomplete"
    )


def cmd_result(args: argparse.Namespace) -> None:
    """Dispatch result diagnostics and explicit evaluation workflows."""
    if args.result_command == "status":
        cmd_result_status(args)
    elif args.result_command == "registry" and args.registry_command == "seed":
        cmd_result_registry_seed(args)
    elif args.result_command == "evaluate":
        from trading.core.evaluation import evaluate_asset_from_cli

        evaluate_asset_from_cli(args.asset)


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
    for event in events:
        if not isinstance(event, Mapping) or event.get("event_type") != "historical_plan":
            continue
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            continue
        plan_id = payload.get("plan_id")
        screen = screens.get(plan_id, {})
        disposition = screen.get("disposition", "historical-screen-pending")
        print(f"{plan_id}: {disposition}")
        print(f"  definition fingerprint: {payload.get('definition_fingerprint', '-')}")
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


def cmd_analyze(args: argparse.Namespace) -> None:
    """滾動窗口績效分析 (Rolling window performance analysis)"""
    from trading.core.performance_analyzer import PerformanceAnalyzer

    strategy = get_experiment(args.experiment)
    analyzer = PerformanceAnalyzer(
        strategy,
        window_years=args.window_years,
        step_months=args.step_months,
    )
    analyzer.run()


def cmd_sync_docs(args: argparse.Namespace) -> None:
    """同步與檢查文件 (Sync and check documentation)"""
    from trading.core.sync_docs import compare_docs_and_results

    compare_docs_and_results()


def cmd_followup_backtest(args: argparse.Namespace) -> None:
    """Backtest the current followup strategy portfolio."""
    from trading.followup_backtest import render_followup_backtest, run_followup_backtest

    result = run_followup_backtest(days=args.days, start=args.start)
    render_followup_backtest(result)
    if not result.strategies or result.all_failed or result.portfolio is None:
        raise SystemExit(1)


def cmd_followup_state(args: argparse.Namespace) -> None:
    """Manage the local controlled-cutover lifecycle without placing orders."""
    from trading.followup import STRATEGIES

    try:
        registry = FollowupLifecycleRegistry(args.path)
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
    manifest_path = args.manifest
    if manifest_path is None and args.experiment is None:
        raise SystemExit("data-only snapshot requires --manifest PATH")
    service = create_default_market_data_service()
    store = create_default_research_data_store()
    definition = None
    if args.experiment is not None:
        experiment = get_experiment(args.experiment)
        run_with_bundle = getattr(experiment, "run_with_bundle", None)
        capture_definition = getattr(experiment, "capture_research_definition", None)
        if not callable(run_with_bundle) or not callable(capture_definition):
            raise SystemExit(
                f"{args.experiment} is not snapshot-aware; formal snapshot preparation "
                "requires run_with_bundle and capture_research_definition"
            )
        captured = capture_definition(create_default_research_definition_store())
        if not isinstance(captured, ResearchDefinitionSnapshot):
            raise SystemExit("capture_research_definition must return ResearchDefinitionSnapshot")
        definition = captured.blob
    primary = MarketDataSeries.yahoo_adjusted_daily(args.symbol)
    auxiliary = [MarketDataSeries.yahoo_adjusted_daily(symbol) for symbol in args.aux]
    for series in (primary, *auxiliary):
        service.refresh(series, mode="full", start=None, end=args.decision)
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
    manifest = store.create_snapshot(
        service.cache,
        requirements,
        SignalDecisionTime.for_primary_session(args.decision),
        definition=definition,
    )
    if manifest_path is None:
        manifest_path = Path("results") / args.experiment / f"{manifest.snapshot_id}.snapshot.json"
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

    # list
    sub.add_parser("list", help="列出所有實驗 (List all experiments)")

    # run
    run_p = sub.add_parser("run", help="執行實驗 (Run experiment(s))")
    run_p.add_argument("experiment", nargs="?", help="實驗名稱 (Experiment name)")
    run_p.add_argument("--all", action="store_true", help="執行全部實驗 (Run all experiments)")
    run_mode = run_p.add_mutually_exclusive_group()
    run_mode.add_argument(
        "--snapshot",
        type=Path,
        help="Run online against a verified current snapshot and advance latest.json",
    )
    run_mode.add_argument(
        "--offline",
        type=Path,
        help="Persist historical output from a verified older snapshot; never update latest.json",
    )
    run_mode.add_argument(
        "--ephemeral",
        action="store_true",
        help="Run diagnostics without changing results or registry state",
    )
    run_mode.add_argument(
        "--legacy",
        action="store_true",
        help="Explicitly persist an unmigrated historical result; never advance latest.json",
    )

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

    # followup-backtest
    followup_backtest_p = sub.add_parser(
        "followup-backtest",
        help="回測目前跟單策略組合 (Backtest current followup portfolio)",
    )
    followup_backtest_p.add_argument(
        "--days",
        type=positive_int,
        default=126,
        help="完整交易日數 (Completed trading sessions, default: 126)",
    )
    followup_backtest_p.add_argument(
        "--start",
        type=iso_date,
        help="開始日期 YYYY-MM-DD；非交易日順延 (Optional start date)",
    )

    # compare
    cmp_p = sub.add_parser("compare", help="比較實驗結果 (Compare experiment results)")
    cmp_p.add_argument(
        "experiments", nargs="+", help="要比較的實驗名稱 (Experiment names to compare)"
    )

    # result diagnostics and explicit evaluation
    result_p = sub.add_parser("result", help="Result validity and trial-history operations")
    result_sub = result_p.add_subparsers(dest="result_command", required=True)
    status_p = result_sub.add_parser("status", help="Read-only result validity diagnostics")
    status_p.add_argument("experiment", nargs="?", help="Experiment name")
    status_p.add_argument("--all", action="store_true", help="Inspect every latest result")
    evaluate_p = result_sub.add_parser(
        "evaluate",
        help="Explicitly refresh stale candidates and produce a complete asset ranking",
    )
    evaluate_p.add_argument("asset", help="Asset ticker, for example SPY")
    registry_p = result_sub.add_parser("registry", help="Experiment trial registry operations")
    registry_sub = registry_p.add_subparsers(dest="registry_command", required=True)
    registry_sub.add_parser("seed", help="Seed discoverable legacy experiments")

    qualification_p = sub.add_parser(
        "qualification",
        help="Read-only Historical and Shadow lifecycle diagnostics",
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

    # analyze
    analyze_p = sub.add_parser(
        "analyze", help="滾動窗口績效分析 (Rolling window performance analysis)"
    )
    analyze_p.add_argument("experiment", help="實驗名稱 (Experiment name)")
    analyze_p.add_argument(
        "--window-years",
        type=int,
        default=2,
        help="窗口大小（年）(Window size in years, default: 2)",
    )
    analyze_p.add_argument(
        "--step-months", type=int, default=6, help="步進（月）(Step size in months, default: 6)"
    )

    # sync-docs
    sub.add_parser(
        "sync-docs",
        help="檢查 Markdown 文件與 latest.json 是否同步 (Check if Markdown docs are in sync with latest.json)",
    )

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
        help="Capture snapshot-aware experiment definition for formal execution",
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
        help=(
            "Tracked result-linked destination; formal default is "
            "results/NAME/<snapshot_id>.snapshot.json"
        ),
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

    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
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
    elif args.command == "followup-backtest":
        cmd_followup_backtest(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "result":
        cmd_result(args)
    elif args.command == "qualification" and args.qualification_command == "status":
        cmd_qualification_status(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "sync-docs":
        cmd_sync_docs(args)
    elif args.command == "freshness":
        from trading.core.freshness import check_freshness

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

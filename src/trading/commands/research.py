"""Workflow-native research CLI handler."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Callable
from datetime import date
from pathlib import Path

from trading.core.data_fetcher import create_default_market_data_service
from trading.market_data import (
    MarketDataAvailabilityError,
    MarketDataBundle,
    MarketDataCoveragePolicy,
    SignalDecisionTime,
)
from trading.research_data import (
    ExperimentTrialDeclaration,
    ExperimentTrialRegistry,
    ResearchDataStore,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
    ResearchRunCoordinator,
    RunMode,
    research_trial_directory,
    trial_registry_path,
)
from trading.research_definitions import (
    ResearchDefinitionRegistry,
    ResearchDefinitionRegistryError,
    WorkflowNativeExecutionError,
    resolve_workflow_policy_set,
)


def register_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    *,
    iso_date: Callable[[str], date],
) -> None:
    """Register workflow-native research commands."""
    research = subparsers.add_parser(
        "research", help="Prepare and execute workflow-native research definitions"
    )
    commands = research.add_subparsers(dest="research_command", required=True)
    commands.add_parser("list", help="List workflow-native family/trial identities")
    snapshot = commands.add_parser("snapshot", help="Capture definition and market-data evidence")
    snapshot.add_argument("identity", help="Exact family/trial identity")
    snapshot.add_argument("--workflow", type=Path, required=True)
    snapshot.add_argument("--decision", type=iso_date, required=True)
    snapshot.add_argument("--manifest", type=Path)
    snapshot.add_argument("--cache-root", type=Path)
    snapshot.add_argument("--reuse-full-refresh", action="store_true")
    run = commands.add_parser("run", help="Execute against an immutable snapshot")
    run.add_argument("identity", help="Exact family/trial identity")
    run.add_argument("--workflow", type=Path, required=True)
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--offline", action="store_true")


def _research_data_store() -> ResearchDataStore:
    return ResearchDataStore(Path(".research-data/blobs"))


def _definition_store() -> ResearchDefinitionStore:
    return ResearchDefinitionStore(Path(".research-data/blobs"))


def _workflow_native_context(identity: str, workflow_path: Path) -> tuple[object, object]:
    definition = ResearchDefinitionRegistry().load(identity)
    policy_set = resolve_workflow_policy_set(workflow_path)
    return definition, policy_set


def _workflow_observation_provenance(
    args: argparse.Namespace,
    policy_set: object,
) -> dict[str, object]:
    """Capture exact workflow-native run coordination and invocation evidence."""
    workflow_path = Path(args.workflow)
    release_path = workflow_path / "RELEASE.json"
    workflow_definition_path = workflow_path / "WORKFLOW.md"
    try:
        release_bytes = release_path.read_bytes()
        workflow_bytes = workflow_definition_path.read_bytes()
        release = json.loads(release_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowNativeExecutionError(
            f"cannot capture workflow release provenance: {exc}"
        ) from exc
    if not isinstance(release, dict):
        raise WorkflowNativeExecutionError("workflow release provenance must be an object")

    source_paths = (
        Path("src/trading/cli.py"),
        Path("src/trading/commands/research.py"),
        Path("src/trading/research_definitions/execution.py"),
        Path("src/trading/research_data/runs.py"),
        Path("src/trading/research_data/result_schema.py"),
    )
    sources: dict[str, object] = {}
    try:
        for path in source_paths:
            content = path.read_text(encoding="utf-8")
            sources[str(path)] = {
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "content": content,
            }
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, UnicodeError, subprocess.CalledProcessError) as exc:
        raise WorkflowNativeExecutionError(
            f"cannot capture orchestration provenance: {exc}"
        ) from exc

    canonical_argv = [
        "trading",
        "research",
        "run",
        args.identity,
        "--workflow",
        str(workflow_path),
        "--manifest",
        str(args.manifest),
    ]
    if args.offline:
        canonical_argv.append("--offline")
    policy_set_identity = getattr(policy_set, "identity", None)
    if not isinstance(policy_set_identity, str):
        raise WorkflowNativeExecutionError("resolved policy set identity is missing")
    return {
        "schema_version": 1,
        "canonical_argv": canonical_argv,
        "working_directory": str(Path.cwd()),
        "workflow": {
            "path": str(workflow_path),
            "workflow": release.get("workflow"),
            "version": release.get("version"),
            "release_sha256": hashlib.sha256(release_bytes).hexdigest(),
            "workflow_sha256": hashlib.sha256(workflow_bytes).hexdigest(),
            "policy_set_identity": policy_set_identity,
        },
        "orchestration": {
            "git_head": completed.stdout.strip(),
            "sources": sources,
        },
    }


def cmd_research(args: argparse.Namespace) -> None:
    """Prepare and execute workflow-native definitions outside the legacy inventory."""
    try:
        if args.research_command == "list":
            for identity in ResearchDefinitionRegistry().list_trials():
                print(identity)
            return
        definition, policy_set = _workflow_native_context(args.identity, args.workflow)
        capture = getattr(definition, "capture_research_definition", None)
        requirements_factory = getattr(definition, "market_data_requirements", None)
        result_name = getattr(definition, "result_name", None)
        if (
            not callable(capture)
            or not callable(requirements_factory)
            or not isinstance(result_name, str)
        ):
            raise WorkflowNativeExecutionError("definition does not implement formal seams")
        captured = capture(_definition_store(), policy_set)
        if not isinstance(captured, ResearchDefinitionSnapshot):
            raise WorkflowNativeExecutionError(
                "capture_research_definition must return ResearchDefinitionSnapshot"
            )
        if args.research_command == "snapshot":
            requirements = MarketDataBundle.validate_requirements(requirements_factory())
            service_kwargs: dict[str, Path] = {}
            if args.cache_root is not None:
                service_kwargs = {
                    "cache_root": args.cache_root,
                    "quarantine_root": args.cache_root.parent
                    / f"{args.cache_root.name}-quarantine",
                }
            service = create_default_market_data_service(**service_kwargs)
            if not args.reuse_full_refresh:
                for requirement in requirements:
                    refresh_kwargs = {"mode": "full", "start": None, "end": args.decision}
                    if requirement.coverage_policy != MarketDataCoveragePolicy.xnys():
                        refresh_kwargs["coverage_policy"] = requirement.coverage_policy
                    service.refresh(requirement.series, **refresh_kwargs)
            store = _research_data_store()
            manifest = store.create_snapshot(
                service.cache,
                requirements,
                SignalDecisionTime.for_primary_session(args.decision),
                definition=captured.blob,
            )
            destination = args.manifest or (
                research_trial_directory(Path("results"), args.identity)
                / f"{manifest.snapshot_id}.snapshot.json"
            )
            path = store.write_manifest(manifest, destination)
            print(f"research snapshot {manifest.snapshot_id} published to {path}")
            if args.reuse_full_refresh:
                print("  market data: reused the current eligible full-refresh generation")
            print(f"  definition fingerprint: {captured.fingerprint}")
            print(f"  policy set: {captured.policy_set_identity}")
            return
        run_with_bundle = getattr(definition, "run_with_bundle", None)
        declare_trial = getattr(definition, "declare_experiment_trial", None)
        if not callable(run_with_bundle) or not callable(declare_trial):
            raise WorkflowNativeExecutionError("definition does not implement formal run seams")
        trial = declare_trial()
        if not isinstance(trial, ExperimentTrialDeclaration):
            raise WorkflowNativeExecutionError(
                "declare_experiment_trial must return ExperimentTrialDeclaration"
            )
        outcome = ResearchRunCoordinator(
            store=_research_data_store(),
            results_root=Path("results"),
            result_directory=research_trial_directory(Path("results"), args.identity),
            trial_registry=ExperimentTrialRegistry(trial_registry_path()),
            experiment_family=trial.family,
            hypothesis=trial.hypothesis,
        ).execute(
            result_name,
            run_with_bundle,
            manifest_path=args.manifest,
            current_definition=captured.blob,
            mode=RunMode.OFFLINE if args.offline else RunMode.ONLINE,
            observation_provenance=_workflow_observation_provenance(args, policy_set),
        )
        print(f"research result published to {outcome.persisted_path}")
        print(f"  definition fingerprint: {captured.fingerprint}")
        print(f"  policy set: {captured.policy_set_identity}")
    except (
        MarketDataAvailabilityError,
        ResearchDefinitionRegistryError,
        WorkflowNativeExecutionError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        raise SystemExit(f"research error: {exc}") from exc

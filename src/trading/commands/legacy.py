"""Explicit legacy CLI namespace and fail-closed retired handlers."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
from pathlib import Path

from trading.experiments import get_experiment, list_experiments
from trading.legacy import results as result_module
from trading.legacy.definition_resolver import resolve_current_definition_fingerprint
from trading.legacy.freshness import check_legacy_freshness
from trading.legacy.results import (
    ResultSource,
    compare_experiments,
    inspect_result,
    latest_result_names,
)
from trading.research_data import ResearchDataStore

RETIREMENT_MESSAGE = (
    "legacy experiment research is retired; use `trading research` with a released workflow"
)


def cmd_list(_args: argparse.Namespace) -> None:
    """List the archived inventory without authorizing execution."""
    experiments = list_experiments()
    print(f"\n  Archived legacy experiments: {len(experiments)}")
    print(f"  {'=' * 40}")
    for name in experiments:
        strategy = get_experiment(name)
        config = strategy.create_config()
        experiment_id = config.experiment_id or ""
        print(f"  - {experiment_id:<10} {name:<30} {config.display_name}")
    print()


def cmd_retired(_args: argparse.Namespace) -> None:
    """Fail closed for every retired mutating or outcome-inspection command."""
    raise SystemExit(RETIREMENT_MESSAGE)


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare retained archived results without refreshing them."""
    compare_experiments(args.experiments)


def cmd_result_status(args: argparse.Namespace) -> None:
    """Show archived latest-result validity without execution."""
    if args.all:
        names = latest_result_names(
            results_dir=result_module.RESULTS_DIR,
            archive_dir=result_module.ARCHIVED_RESULTS_DIR,
            include_archive=True,
        )
    elif args.experiment:
        names = [args.experiment]
    else:
        raise SystemExit("result status requires an experiment name or --all")

    store = ResearchDataStore(Path(".research-data/blobs"))
    for name in names:
        record = inspect_result(
            name,
            results_dir=result_module.RESULTS_DIR,
            archive_dir=result_module.ARCHIVED_RESULTS_DIR,
            allow_archive=True,
            store=store,
            current_definition_fingerprint=resolve_current_definition_fingerprint(name),
        )
        if record is None:
            print(f"{name}: no latest result")
            continue
        source = f" [{record.source.value}]" if record.source is ResultSource.LEGACY_ARCHIVE else ""
        print(f"{name}: {record.validity.status.value}{source}")
        if record.result.payload:
            payload = record.result.payload
            print(f"  schema version: {payload.get('schema_version', 'legacy')}")
            print(f"  data cutoff: {payload.get('data_cutoff', '-')}")
            print(f"  definition fingerprint: {payload.get('definition_fingerprint', '-')}")
        for reason in record.validity.reasons:
            print(f"  reason: {reason}")


def cmd_result(args: argparse.Namespace) -> None:
    """Dispatch read-only status or fail-closed retired result operations."""
    if args.result_command == "status":
        cmd_result_status(args)
        return
    cmd_retired(args)


def cmd_freshness(_args: argparse.Namespace) -> None:
    """Audit archived overview and result freshness."""
    check_legacy_freshness()


def dispatch(args: argparse.Namespace) -> None:
    """Dispatch the explicit ``trading legacy`` namespace."""
    command = args.legacy_command
    if command == "list":
        cmd_list(args)
    elif command == "compare":
        cmd_compare(args)
    elif command == "result":
        cmd_result(args)
    elif command == "freshness":
        cmd_freshness(args)
    else:
        cmd_retired(args)


def _add_result_parser(parent: argparse.ArgumentParser) -> None:
    result_sub = parent.add_subparsers(dest="result_command", required=True)
    status = result_sub.add_parser("status", help="Read-only archived-result validity diagnostics")
    status.add_argument("experiment", nargs="?", help="Archived experiment name")
    status.add_argument("--all", action="store_true", help="Inspect every archived latest result")
    evaluate = result_sub.add_parser("evaluate", help="Retired evaluation (always fails closed)")
    evaluate.add_argument("asset", help="Asset ticker, for example SPY")
    registry = result_sub.add_parser("registry", help="Retired trial registry operations")
    registry.add_subparsers(dest="registry_command", required=True).add_parser(
        "seed", help="Retired registry mutation (always fails closed)"
    )


def register_namespace(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    *,
    iso_date: Callable[[str], date],
    positive_int: Callable[[str], int],
) -> None:
    """Register the explicit ``trading legacy`` command tree."""
    legacy = subparsers.add_parser("legacy", help="Inspect the retired legacy experiment system")
    commands = legacy.add_subparsers(dest="legacy_command", required=True)
    commands.add_parser("list", help="List the archived experiment inventory")
    run = commands.add_parser("run", help="Retired runner (always fails closed)")
    run.add_argument("experiment", nargs="?")
    run.add_argument("--all", action="store_true")
    compare = commands.add_parser("compare", help="Compare archived latest results")
    compare.add_argument("experiments", nargs="+")
    result = commands.add_parser("result", help="Archived result diagnostics")
    _add_result_parser(result)
    analyze = commands.add_parser("analyze", help="Retired rolling analysis (always fails closed)")
    analyze.add_argument("experiment")
    commands.add_parser("sync-docs", help="Retired documentation sync (always fails closed)")
    backtest = commands.add_parser(
        "followup-backtest", help="Retired portfolio backtest (always fails closed)"
    )
    backtest.add_argument("--days", type=positive_int, default=126)
    backtest.add_argument("--start", type=iso_date)
    commands.add_parser("freshness", help="Audit archived knowledge and result freshness")

"""
統一 CLI 入口 (Unified CLI Entry Point)
支援實驗、跟單與分析子命令。
Supports experiment, followup, and analysis subcommands.
"""

import argparse
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

from trading.core.data_fetcher import create_default_market_data_service
from trading.core.results import compare_experiments, save_result
from trading.experiments import get_experiment, list_experiments
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.research_data import (
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
            if not callable(run_with_bundle) or not callable(capture_definition):
                if default_formal:
                    raise SystemExit(
                        "persisted runs require a snapshot-aware prepared manifest or "
                        "--snapshot MANIFEST; use --legacy only for unmigrated experiments"
                    )
                raise SystemExit(
                    f"{name} is not snapshot-aware; formal execution requires "
                    "run_with_bundle and capture_research_definition"
                )
            definition = capture_definition(create_default_research_definition_store())
            if not isinstance(definition, ResearchDefinitionSnapshot):
                raise SystemExit(
                    "capture_research_definition must return ResearchDefinitionSnapshot"
                )
            research_store = create_default_research_data_store()
            if default_formal:
                formal_manifest = research_store.latest_manifest_for_definition(
                    Path("results") / name,
                    definition.blob,
                )
            coordinator = ResearchRunCoordinator(
                store=research_store,
                results_root=Path("results"),
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
        help="Explicitly persist an unmigrated result without Phase 2 evidence",
    )

    # followup
    sub.add_parser("followup", help="產生跟單訊號報告 (Generate Firstrade trading signals)")

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

        run_followup()
    elif args.command == "followup-backtest":
        cmd_followup_backtest(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "sync-docs":
        cmd_sync_docs(args)
    elif args.command == "freshness":
        from trading.core.freshness import check_freshness

        check_freshness()
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

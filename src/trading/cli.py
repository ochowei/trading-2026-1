"""
統一 CLI 入口 (Unified CLI Entry Point)
支援實驗、跟單與分析子命令。
Supports experiment, followup, and analysis subcommands.
"""

import argparse
import logging
import sys
from datetime import date

from trading.core.data_fetcher import create_default_market_data_service
from trading.core.results import compare_experiments, save_result
from trading.experiments import get_experiment, list_experiments
from trading.market_data import MarketDataSeries

# 設定日誌格式 (Configure logging format)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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

    for name in names:
        logger.info(f"執行實驗: {name} (Running experiment: {name})")
        strategy = get_experiment(name)
        result = strategy.run()

        # 儲存結果 (Save results)
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
    else:
        # 無子命令時顯示幫助 (Show help when no subcommand)
        parser.print_help()
        sys.exit(0)

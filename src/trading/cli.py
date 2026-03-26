"""
統一 CLI 入口 (Unified CLI Entry Point)
支援 list / run / compare 子命令。
Supports list / run / compare subcommands.
"""

import argparse
import logging
import sys

from trading.core.results import compare_experiments, save_result
from trading.experiments import get_experiment, list_experiments

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
    print(f"  {'='*40}")
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


def main() -> None:
    """CLI 主程式 (CLI main)"""
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

    # compare
    cmp_p = sub.add_parser("compare", help="比較實驗結果 (Compare experiment results)")
    cmp_p.add_argument("experiments", nargs="+", help="要比較的實驗名稱 (Experiment names to compare)")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "followup":
        from trading.followup import run_followup
        run_followup()
    elif args.command == "compare":
        cmd_compare(args)
    else:
        # 無子命令時顯示幫助 (Show help when no subcommand)
        parser.print_help()
        sys.exit(0)

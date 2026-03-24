"""
掃描器主程式 (Scanner Main Module)
"""

import logging
import sys

from trading_tw.scanner.tqqq_strategy import TQQQStrategy

# 設定日誌格式 (Configure logging format)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_scanner() -> None:
    """
    CLI 進入點 (CLI entry point)

    用法 (Usage):
        trading-tw                              # 執行 TQQQ 策略
        trading-tw --strategy tqqq              # 執行 TQQQ 策略
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="美股交易策略掃描器 (US Stock Trading Scanner)"
    )
    parser.add_argument(
        "--strategy", choices=["tqqq"], default="tqqq",
        help="策略選擇 (Strategy: tqqq=TQQQ 恐慌抄底)",
    )
    parser.add_argument(
        "--tickers", nargs="+", default=None,
        help="要掃描的標的清單 (保留此參數以相容 CLI 呼叫，但不影響 TQQQ 策略)",
    )
    parser.add_argument(
        "--period", default="5y",
        help="歷史資料期間 (保留此參數以相容 CLI 呼叫，但不影響 TQQQ 策略)",
    )
    args = parser.parse_args()

    if args.strategy == "tqqq":
        strategy = TQQQStrategy()
        strategy.run()


if __name__ == "__main__":
    run_scanner()

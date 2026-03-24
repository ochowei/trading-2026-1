"""
掃描器主程式 (Scanner Main Module)
整合所有元件：資料擷取 → 訊號偵測 → 回測 → 報表。
Orchestrates all components: DataFetcher → SignalDetector → Backtester → Reporter.
"""

import logging
import sys

import pandas as pd

from trading_tw.scanner.backtester import Backtester
from trading_tw.scanner.config import DEFAULT_TICKERS
from trading_tw.scanner.data_fetcher import DataFetcher
from trading_tw.scanner.reporter import Reporter
from trading_tw.scanner.signal_detector import SignalDetector

# 設定日誌格式 (Configure logging format)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ScannerApp:
    """
    掃描器應用程式 (Scanner Application)
    主要的協調器，串接資料下載、訊號偵測、回測與報表輸出。
    Main orchestrator that chains data fetching, signal detection, backtesting, and reporting.
    """

    def __init__(
        self,
        tickers: list[str] | None = None,
        period: str = "5y",
    ):
        """
        初始化掃描器 (Initialize scanner)

        Args:
            tickers: 要掃描的標的清單，預設使用 DEFAULT_TICKERS
                     (Tickers to scan, defaults to DEFAULT_TICKERS)
            period: 歷史資料期間 (Historical data period)
        """
        self.tickers = tickers or DEFAULT_TICKERS
        self.fetcher = DataFetcher(period=period)
        self.detector = SignalDetector()
        self.backtester = Backtester()
        self.reporter = Reporter()

    def run(self, tickers: list[str] | None = None) -> pd.DataFrame:
        """
        執行完整掃描流程 (Run full scanning pipeline)

        流程 (Pipeline):
        1. 下載歷史數據 (Fetch historical data)
        2. 計算技術指標 (Compute indicators)
        3. 偵測訊號 (Detect signals)
        4. 回測驗證 (Backtest validation)
        5. 輸出報表 (Generate report)

        Args:
            tickers: 覆蓋初始化時的標的清單 (Override tickers from init)

        Returns:
            Summary DataFrame
        """
        scan_tickers = tickers or self.tickers

        print(f"\n掃描標的 (Scanning tickers): {', '.join(scan_tickers)}")
        print(f"標的數量 (Total): {len(scan_tickers)}\n")

        # Step 1: 下載數據 (Fetch data)
        logger.info("Step 1/4: 下載歷史數據 (Fetching historical data)...")
        data = self.fetcher.fetch_all(scan_tickers)

        if not data:
            logger.error("無法取得任何數據，程式終止 (No data fetched, aborting)")
            sys.exit(1)

        # Step 2 & 3: 計算指標 + 偵測訊號 (Compute indicators + detect signals)
        logger.info("Step 2/4: 計算技術指標與偵測訊號 (Computing indicators & detecting signals)...")
        processed_data: dict[str, pd.DataFrame] = {}

        for ticker, df in data.items():
            try:
                df_with_indicators = self.detector.compute_indicators(df)
                df_with_signals = self.detector.detect_signals(df_with_indicators, ticker)
                processed_data[ticker] = df_with_signals
            except Exception as e:
                logger.error(
                    f"{ticker} 指標計算失敗 (Indicator computation failed): {e}"
                )

        # Step 4: 回測 (Backtest)
        logger.info("Step 3/4: 執行回測 (Running backtests)...")
        results: list[dict] = []

        for ticker, df in processed_data.items():
            try:
                result = self.backtester.run(df, ticker)
                results.append(result)
            except Exception as e:
                logger.error(f"{ticker} 回測失敗 (Backtest failed): {e}")

        # Step 5: 輸出報表 (Generate report)
        logger.info("Step 4/4: 產生報表 (Generating report)...")
        summary_df = self.reporter.generate_summary(results)
        today_signals = self.reporter.check_today_signals(processed_data)
        self.reporter.print_report(summary_df, today_signals, results)

        return summary_df


def run_scanner() -> None:
    """CLI 進入點 (CLI entry point)"""
    app = ScannerApp()
    app.run()


if __name__ == "__main__":
    run_scanner()

"""
TQQQ 恐慌抄底策略主程式 (TQQQ Capitulation Buy Strategy)
串接資料擷取 → 訊號偵測 → 回測 → 報表輸出。
Orchestrates: DataFetcher → TQQQSignalDetector → TQQQBacktester → Report.
"""

import logging

import pandas as pd

from trading_tw.scanner.data_fetcher import DataFetcher
from trading_tw.scanner.tqqq_backtester import TQQQBacktester
from trading_tw.scanner.tqqq_config import (
    TQQQ_DATA_PERIOD,
    TQQQ_DRAWDOWN_THRESHOLD,
    TQQQ_HOLDING_DAYS,
    TQQQ_PROFIT_TARGET,
    TQQQ_RSI_PERIOD,
    TQQQ_RSI_THRESHOLD,
    TQQQ_STOP_LOSS,
    TQQQ_TICKER,
    TQQQ_VOLUME_MULTIPLIER,
)
from trading_tw.scanner.tqqq_signal_detector import TQQQSignalDetector

logger = logging.getLogger(__name__)


class TQQQStrategy:
    """
    TQQQ 恐慌抄底策略 (TQQQ Capitulation Buy Strategy)

    專為 TQQQ 設計的低頻高勝率策略，每年約 3-5 次訊號。
    Low-frequency, high-win-rate strategy designed for TQQQ, ~3-5 signals/year.
    """

    def __init__(self, period: str = TQQQ_DATA_PERIOD):
        self.fetcher = DataFetcher(period=period)
        self.detector = TQQQSignalDetector()
        self.backtester = TQQQBacktester()

    def run(self) -> dict:
        """
        執行 TQQQ 恐慌抄底策略完整流程 (Run full TQQQ strategy pipeline)

        Returns:
            Backtest result dict
        """
        separator = "=" * 80

        print(f"\n{separator}")
        print("  TQQQ 恐慌抄底策略 — Capitulation Buy Strategy")
        print(f"{separator}\n")

        # Step 1: 下載 TQQQ 數據 (Fetch TQQQ data)
        logger.info("Step 1/3: 下載 TQQQ 歷史數據 (Fetching TQQQ data)...")
        data = self.fetcher.fetch_all([TQQQ_TICKER])

        if TQQQ_TICKER not in data:
            logger.error("無法取得 TQQQ 數據 (Failed to fetch TQQQ data)")
            return self.backtester._empty_result()

        df = data[TQQQ_TICKER]
        print(f"  資料期間: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  資料筆數: {len(df)} 個交易日\n")

        # Step 2: 計算指標 + 偵測訊號 (Compute indicators + detect signals)
        logger.info("Step 2/3: 計算指標與偵測訊號 (Computing indicators & detecting signals)...")
        df = self.detector.compute_indicators(df)
        df = self.detector.detect_signals(df)

        # Step 3: 回測 (Backtest)
        logger.info("Step 3/3: 執行回測 (Running backtest)...")
        result = self.backtester.run(df)

        # 輸出報表 (Print report)
        self._print_report(result, df)

        return result

    def _print_report(self, result: dict, df: pd.DataFrame) -> None:
        """印出 TQQQ 策略報表 (Print TQQQ strategy report)"""
        separator = "=" * 80
        thin_sep = "-" * 80

        # 策略參數 (Strategy parameters)
        print(f"\n{thin_sep}")
        print("  策略參數 (Strategy Parameters)")
        print(f"{thin_sep}")
        print(f"  回撤閾值 (Drawdown threshold):  {TQQQ_DRAWDOWN_THRESHOLD:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({TQQQ_RSI_PERIOD}) < {TQQQ_RSI_THRESHOLD}")
        print(f"  成交量倍數 (Volume multiplier):  {TQQQ_VOLUME_MULTIPLIER}x")
        print(f"  獲利目標 (Profit target):        +{TQQQ_PROFIT_TARGET:.0%}")
        print(f"  停損 (Stop-loss):                {TQQQ_STOP_LOSS:.0%}")
        print(f"  最長持倉 (Max holding):          {TQQQ_HOLDING_DAYS} 天")

        trades = result["trades"]

        if not trades:
            print(f"\n{separator}")
            print("  無訊號觸發 (No signals detected)")
            print(f"{separator}\n")
            return

        # 彙總績效 (Aggregate performance)
        print(f"\n{thin_sep}")
        print("  回測績效摘要 (Backtest Performance Summary)")
        print(f"{thin_sep}")
        print(f"  總訊號數 (Total signals):        {result['total_signals']}")
        print(f"  每年平均 (Avg per year):          {self._signals_per_year(trades, df):.1f}")
        print(f"  獲利次數 (Wins):                 {result['wins']}")
        print(f"  勝率 (Win rate):                 {result['win_rate']:.1%}")
        print(f"  平均報酬 (Avg return):           {result['avg_return_pct']:+.2f}%")
        print(f"  報酬標準差 (Std return):         {result['std_return_pct']:.2f}%")
        print(f"  累計報酬 (Cumulative return):    {result['cumulative_return_pct']:+.2f}%")
        print(f"  平均持倉 (Avg holding days):     {result['avg_holding_days']:.1f} 天")
        print(f"  最大單筆回撤 (Max drawdown):     {result['max_drawdown_pct']:.2f}%")
        print(f"  最大連續虧損 (Max consec. loss): {result['max_consecutive_losses']}")

        # 出場方式統計 (Exit type breakdown)
        print(f"\n  出場方式 (Exit breakdown):")
        print(f"    達標出場 (Target hit):         {result['target_exits']}")
        print(f"    停損出場 (Stop-loss):          {result['stop_loss_exits']}")
        print(f"    到期出場 (Time expiry):        {result['time_expiry_exits']}")

        # 逐筆交易明細 (Trade details)
        print(f"\n{thin_sep}")
        print("  逐筆交易明細 (Trade Details)")
        print(f"{thin_sep}")
        print(f"  {'日期':<12} {'進場':>8} {'出場':>8} {'報酬':>8} {'持倉':>4} {'出場方式':<12}")
        print(f"  {'Date':<12} {'Entry':>8} {'Exit':>8} {'Return':>8} {'Days':>4} {'Exit Type':<12}")
        print(f"  {'-'*60}")

        exit_type_labels = {
            "target": "達標 Target",
            "stop_loss": "停損 Stop",
            "time_expiry": "到期 Expiry",
            "no_data": "無資料 N/A",
        }

        for t in trades:
            label = exit_type_labels.get(t["exit_type"], t["exit_type"])
            print(
                f"  {t['date']:<12} "
                f"{t['entry']:>8.2f} "
                f"{t['exit']:>8.2f} "
                f"{t['return_pct']:>+7.2f}% "
                f"{t['holding_days']:>4d} "
                f"{label:<12}"
            )

        # 今日訊號檢查 (Today's signal check)
        print(f"\n{separator}")
        today = pd.Timestamp.now().normalize()
        latest_date = df.index[-1]
        if latest_date >= today and df.loc[latest_date, "Signal"]:
            print("  *** 今日 TQQQ 觸發恐慌抄底訊號！ ***")
            print("  *** TODAY: TQQQ Capitulation Buy Signal TRIGGERED! ***")
        else:
            print("  今日 TQQQ 無訊號 (No TQQQ signal today)")
        print(f"{separator}\n")

    @staticmethod
    def _signals_per_year(trades: list[dict], df: pd.DataFrame) -> float:
        """計算每年平均訊號數 (Calculate average signals per year)"""
        if not trades or df.empty:
            return 0.0
        first_date = df.index[0]
        last_date = df.index[-1]
        years = (last_date - first_date).days / 365.25
        if years <= 0:
            return 0.0
        return len(trades) / years

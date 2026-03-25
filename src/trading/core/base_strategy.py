"""
策略基礎類別 (Base Strategy)
提供通用的 run 流程：fetch → indicators → split parts → signals → backtest → report。
Provides the standard pipeline: fetch → indicators → split parts → signals → backtest → report.
"""

import logging
from abc import ABC, abstractmethod

import pandas as pd

from trading.core.base_backtester import BaseBacktester
from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    策略基礎類別 (Base Strategy)

    子類需實作 create_config() 和 create_detector()。
    Subclasses must implement create_config() and create_detector().
    BaseStrategy.run() 提供完整的回測流程，大多數實驗不需要覆寫。
    """

    @abstractmethod
    def create_config(self) -> ExperimentConfig:
        """建立實驗配置 (Create experiment config)"""
        ...

    @abstractmethod
    def create_detector(self) -> BaseSignalDetector:
        """建立訊號偵測器 (Create signal detector)"""
        ...

    def create_backtester(self, config: ExperimentConfig) -> BaseBacktester:
        """建立回測引擎（預設使用通用引擎，可覆寫）"""
        return BaseBacktester(config)

    def run(self) -> dict:
        """
        執行完整策略流程 (Run full strategy pipeline)

        Returns:
            dict with 'part_a', 'part_b', 'part_c' backtest results
        """
        config = self.create_config()
        detector = self.create_detector()
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載數據 (Fetch data)
        logger.info(f"Step 1/3: 下載數據 (Fetching data for {config.tickers})...")
        data = fetcher.fetch_all(config.tickers)

        # 處理每個標的（目前大多數策略只有一個）
        # Process each ticker (most strategies have just one)
        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error(f"無法取得 {primary_ticker} 數據 (Failed to fetch {primary_ticker} data)")
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]
        print(f"  原始資料期間: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  原始資料筆數: {len(df)} 個交易日\n")

        # Step 2: 計算指標 (Compute indicators on full data)
        logger.info("Step 2/3: 計算指標與偵測訊號 (Computing indicators & detecting signals)...")
        df = detector.compute_indicators(df)

        # Step 3: 分區間回測 (Split into parts and backtest)
        logger.info("Step 3/3: 分區間回測 (Running backtests for each part)...")

        parts = config.get_parts()
        # Part C end: 空字串表示至今
        parts_resolved = []
        for label, start, end in parts:
            if not end:
                end = df.index[-1].strftime("%Y-%m-%d")
            parts_resolved.append((label, start, end))

        results = {}
        for label, start, end in parts_resolved:
            df_part = df.loc[start:end].copy()
            if df_part.empty:
                logger.warning(f"{label}: 無資料 (no data)")
                results[label] = backtester._empty_result()
                continue

            df_part = detector.detect_signals(df_part)
            result = backtester.run(df_part)
            results[label] = result

            self._print_part_report(label, start, end, result, df_part, config)

        # 印出比較表 (Print comparison table)
        self._print_comparison(results)

        # 今日訊號檢查 (Today's signal check)
        self._print_today_signal(df, detector, config)

        return {
            "metadata": {
                "execution_time": pd.Timestamp.now().isoformat()
            },
            "part_a": results.get("Part A (In-Sample)", backtester._empty_result()),
            "part_b": results.get("Part B (Out-of-Sample)", backtester._empty_result()),
            "part_c": results.get("Part C (Live)", backtester._empty_result()),
        }

    def _print_part_report(
        self, label: str, start: str, end: str, result: dict,
        df: pd.DataFrame, config: ExperimentConfig
    ) -> None:
        """印出單一區間的報表 (Print report for one backtest period)"""
        separator = "=" * 80
        thin_sep = "-" * 80

        print(f"\n{separator}")
        print(f"  {label}: {start} ~ {end}")
        print(f"  資料筆數: {len(df)} 個交易日")
        print(f"{separator}")

        # 策略參數（只在第一個 Part 印）
        if "Part A" in label:
            print(f"\n{thin_sep}")
            print("  策略參數 (Strategy Parameters)")
            print(f"{thin_sep}")
            self._print_strategy_params(config)

        trades = result["trades"]

        if not trades:
            print(f"\n  無訊號觸發 (No signals detected)\n")
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
        print(f"  {'進場日期':<12} {'出場日期':<12} {'進場':>8} {'出場':>8} {'報酬':>8} {'持倉':>4} {'出場方式':<12}")
        print(f"  {'Entry Date':<12} {'Exit Date':<12} {'Entry':>8} {'Exit':>8} {'Return':>8} {'Days':>4} {'Exit Type':<12}")
        print(f"  {'-'*72}")

        exit_type_labels = {
            "target": "達標 Target",
            "stop_loss": "停損 Stop",
            "time_expiry": "到期 Expiry",
            "no_data": "無資料 N/A",
        }

        for t in trades:
            label_t = exit_type_labels.get(t["exit_type"], t["exit_type"])
            print(
                f"  {t['date']:<12} "
                f"{t['exit_date']:<12} "
                f"{t['entry']:>8.2f} "
                f"{t['exit']:>8.2f} "
                f"{t['return_pct']:>+7.2f}% "
                f"{t['holding_days']:>4d} "
                f"{label_t:<12}"
            )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        """印出策略參數（子類可覆寫以顯示額外參數）"""
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

    def _print_comparison(self, results: dict) -> None:
        """印出 Part A / B / C 比較表 (Print comparison table)"""
        separator = "=" * 80
        thin_sep = "-" * 80

        keys = list(results.keys())
        if len(keys) < 2:
            return

        print(f"\n{separator}")
        print("  績效比較 (Performance Comparison)")
        print(f"{separator}")

        header = f"  {'指標 (Metric)':<36}"
        for k in keys:
            short = k.split(" (")[0]
            header += f" {short:>12}"
        print(header)
        print(f"  {thin_sep}")

        rows = [
            ("總訊號數 (Total signals)", "total_signals", "d"),
            ("獲利次數 (Wins)", "wins", "d"),
            ("勝率 (Win rate)", "win_rate", ".1%"),
            ("平均報酬 (Avg return %)", "avg_return_pct", ".2f"),
            ("累計報酬 (Cumulative %)", "cumulative_return_pct", ".2f"),
            ("平均持倉天數 (Avg hold)", "avg_holding_days", ".1f"),
            ("最大回撤 (Max DD %)", "max_drawdown_pct", ".2f"),
            ("最大連續虧損 (Max consec.)", "max_consecutive_losses", "d"),
        ]

        for label, key, fmt in rows:
            line = f"  {label:<36}"
            for k in keys:
                val = results[k][key]
                line += f" {f'{val:{fmt}}':>12}"
            print(line)

        print()

    def _print_today_signal(
        self, df: pd.DataFrame, detector: BaseSignalDetector,
        config: ExperimentConfig
    ) -> None:
        """今日訊號檢查 (Today's signal check)"""
        separator = "=" * 80

        df_recent = detector.detect_signals(df.copy())

        print(f"{separator}")
        today = pd.Timestamp.now().normalize()
        latest_date = df_recent.index[-1]
        ticker_str = ", ".join(config.tickers)
        if latest_date >= today and df_recent.loc[latest_date, "Signal"]:
            print(f"  *** 今日 {ticker_str} 觸發訊號！ ***")
            print(f"  *** TODAY: {ticker_str} Signal TRIGGERED! ***")
        else:
            print(f"  今日 {ticker_str} 無訊號 (No {ticker_str} signal today)")
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

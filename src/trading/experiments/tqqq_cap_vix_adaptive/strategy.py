"""
TQQQ VIX 適應性策略 (TQQQ VIX Adaptive Strategy)
軟性 VIX + 適應性出場：VIX >= 20，獲利目標 +8%，追蹤停利 -6%，持倉 10 天。
Filters capitulation signals to only enter when VIX >= 20, with adaptive exit.
"""

import logging

import pandas as pd

from trading.core.base_backtester import BaseBacktester
from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.data_fetcher import DataFetcher
from trading.experiments.tqqq_cap_vix_adaptive.config import (
    TQQQCapVixAdaptiveConfig,
    create_default_config,
)
from trading.experiments.tqqq_cap_vix_adaptive.signal_detector import TQQQCapVixAdaptiveDetector
from trading.experiments.tqqq_cap_wider_exit.backtester import TrailingStopBacktester

logger = logging.getLogger(__name__)


class TQQQCapVixAdaptiveStrategy(BaseStrategy):
    """
    TQQQ VIX 適應性策略 (TQQQ VIX Adaptive Strategy)

    假設：軟性 VIX 過濾 (>= 20) 結合適應性出場 (+8% 獲利目標, -6% 追蹤停利) 能取得平衡。
    Hypothesis: Soft VIX filter (>= 20) combined with adaptive exit (+8% target, -6% trailing stop)
    provides a better balance of signal count and quality.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapVixAdaptiveDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> BaseBacktester:
        # 重用 TQQQ-003 的追蹤停利回測器 (Reuse TrailingStopBacktester from TQQQ-003)
        return TrailingStopBacktester(config)  # type: ignore

    def run(self) -> dict:
        """
        覆寫 run() 以在 fetch 後合併 VIX 資料至 TQQQ DataFrame。
        Overrides run() to merge VIX data onto TQQQ DataFrame after fetching.
        """
        config = create_default_config()
        detector = TQQQCapVixAdaptiveDetector(config)
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載 TQQQ 和 VIX 數據
        logger.info(f"Step 1/3: 下載數據 (Fetching data for {config.tickers} + {config.vix_ticker})...")
        all_tickers = config.tickers + [config.vix_ticker]
        data = fetcher.fetch_all(all_tickers)

        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error(f"無法取得 {primary_ticker} 數據")
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]

        # 合併 VIX 資料 (Merge VIX data onto TQQQ DataFrame)
        if config.vix_ticker in data:
            vix_df = data[config.vix_ticker]
            df["VIX"] = vix_df["Close"].reindex(df.index, method="ffill")
            logger.info(
                f"[VixAdaptive] VIX 資料已合併，範圍 {df['VIX'].min():.1f} ~ {df['VIX'].max():.1f} "
                f"(VIX merged, range {df['VIX'].min():.1f}-{df['VIX'].max():.1f})"
            )
        else:
            logger.warning(
                f"[VixAdaptive] 無法取得 {config.vix_ticker} 數據，VIX 過濾將被跳過 "
                f"(Failed to fetch {config.vix_ticker}, VIX filter will be skipped)"
            )

        print(f"  原始資料期間: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  原始資料筆數: {len(df)} 個交易日\n")

        # Step 2: 計算指標與偵測訊號 (Compute indicators & detect signals globally)
        logger.info("Step 2/3: 計算指標與偵測訊號...")
        df = detector.compute_indicators(df)
        df = detector.detect_signals(df)

        # Step 3: 分區間回測 (Split and backtest)
        logger.info("Step 3/3: 分區間回測...")

        parts = config.get_parts()
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

            # Evaluate backtest using the global indicators/signals on df_part
            result = backtester.run(df_part)
            results[label] = result

            self._print_part_report(label, start, end, result, df_part, config)

        self._print_comparison(results)
        self._print_today_signal(df, detector, config)

        return {
            "part_a": results.get("Part A (In-Sample)", backtester._empty_result()),
            "part_b": results.get("Part B (Out-of-Sample)", backtester._empty_result()),
            "part_c": results.get("Part C (Live)", backtester._empty_result()),
        }

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapVixAdaptiveConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  VIX 軟性門檻 (Soft VIX thr):     >= {config.vix_threshold}")
        print(f"  獲利目標 (Profit target):        +{config.profit_target*100:.0f}%")
        print(f"  追蹤停利 (Trailing stop):        {config.trailing_stop_pct*100:.0f}% from peak")
        print(f"  停損 (Stop-loss):                {config.stop_loss*100:.0f}%")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

    def _print_part_report(
        self, label: str, start: str, end: str, result: dict,
        df: pd.DataFrame, config: ExperimentConfig
    ) -> None:
        """覆寫以在出場統計與交易明細中加入追蹤停利類型"""
        # 呼叫父類報表
        super()._print_part_report(label, start, end, result, df, config)

        # 在出場統計後補印追蹤停利數量
        trailing_exits = result.get("trailing_stop_exits", 0)
        if trailing_exits > 0 and result.get("trades"):
            print(f"    追蹤停利 (Trailing stop):      {trailing_exits}")

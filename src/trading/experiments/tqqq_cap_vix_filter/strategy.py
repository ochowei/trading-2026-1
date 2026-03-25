"""
TQQQ VIX 過濾策略 (TQQQ VIX Regime Filter Strategy)
在原始恐慌抄底訊號基礎上，只在 VIX > 25 時進場，過濾低恐慌環境的弱勢訊號。
Filters capitulation signals to only enter when VIX > 25, eliminating weak signals in low-fear environments.
"""

import logging


from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.data_fetcher import DataFetcher
from trading.experiments.tqqq_cap_vix_filter.config import (
    TQQQCapVixFilterConfig,
    create_default_config,
)
from trading.experiments.tqqq_cap_vix_filter.signal_detector import TQQQCapVixFilterDetector

logger = logging.getLogger(__name__)


class TQQQCapVixFilterStrategy(BaseStrategy):
    """
    TQQQ VIX 過濾策略 (TQQQ VIX Regime Filter Strategy)

    假設：VIX > 25 的回撤訊號代表真正市場恐慌，反彈力道更強。
    Hypothesis: Signals during VIX > 25 represent genuine panic with stronger mean-reversion potential.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapVixFilterDetector(create_default_config())

    def run(self) -> dict:
        """
        覆寫 run() 以在 fetch 後合併 VIX 資料至 TQQQ DataFrame。
        Overrides run() to merge VIX data onto TQQQ DataFrame after fetching.
        """
        config = create_default_config()
        detector = TQQQCapVixFilterDetector(config)
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
                f"[VixFilter] VIX 資料已合併，範圍 {df['VIX'].min():.1f} ~ {df['VIX'].max():.1f} "
                f"(VIX merged, range {df['VIX'].min():.1f}-{df['VIX'].max():.1f})"
            )
        else:
            logger.warning(
                f"[VixFilter] 無法取得 {config.vix_ticker} 數據，VIX 過濾將被跳過 "
                f"(Failed to fetch {config.vix_ticker}, VIX filter will be skipped)"
            )

        print(f"  原始資料期間: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  原始資料筆數: {len(df)} 個交易日\n")

        # Step 2: 計算指標
        logger.info("Step 2/3: 計算指標與偵測訊號...")
        df = detector.compute_indicators(df)

        # Step 3: 分區間回測
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

            df_part = detector.detect_signals(df_part)
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
        if not isinstance(config, TQQQCapVixFilterConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  VIX 門檻 (VIX threshold):        > {config.vix_threshold}")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

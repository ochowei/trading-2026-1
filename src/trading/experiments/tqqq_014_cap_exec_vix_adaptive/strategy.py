"""
TQQQ VIX 自適應出場 + 成交模型策略 (TQQQ VIX-Adaptive Exit + Execution Model Strategy)
根據訊號日 VIX 水準動態調整出場參數，以適應不同恐慌程度的市場環境。
Dynamically adjusts exit parameters based on VIX level at signal time.
"""

import logging

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.backtester import VIXAdaptiveBacktester
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.config import (
    TQQQVixAdaptiveConfig,
    create_default_config,
)

logger = logging.getLogger(__name__)


class TQQQVixAdaptiveStrategy(ExecutionModelStrategy):
    """
    TQQQ VIX 自適應出場 + 成交模型策略 (TQQQ-014)

    訊號邏輯: 與 TQQQ-010 完全相同（基線三條件進場）
    出場邏輯: 根據訊號日 VIX 水準動態選擇 TP/SL/持倉天數
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> VIXAdaptiveBacktester:
        slippage = 0.001
        if isinstance(config, TQQQVixAdaptiveConfig):
            slippage = config.slippage_pct
        return VIXAdaptiveBacktester(config, slippage_pct=slippage)

    def run(self) -> dict:
        """覆寫 run() 以合併 VIX 資料"""
        config = create_default_config()
        detector = TQQQSignalDetector(config)
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        logger.info(f"Step 1/3: Fetching data for {config.tickers} + {config.vix_ticker}...")
        all_tickers = config.tickers + [config.vix_ticker]
        data = fetcher.fetch_all(all_tickers)

        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error(f"Cannot fetch {primary_ticker} data")
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]

        if config.vix_ticker in data:
            vix_df = data[config.vix_ticker]
            df["VIX"] = vix_df["Close"].reindex(df.index, method="ffill")
            logger.info(
                f"[VixAdaptive] VIX merged, range {df['VIX'].min():.1f}-{df['VIX'].max():.1f}"
            )
        else:
            logger.warning(
                f"[VixAdaptive] Failed to fetch {config.vix_ticker}, "
                "will use fallback VIX=30.0 for all signals"
            )

        print(
            f"  Data range: {df.index[0].strftime('%Y-%m-%d')} ~ "
            f"{df.index[-1].strftime('%Y-%m-%d')}"
        )
        print(f"  Trading days: {len(df)}\n")

        logger.info("Step 2/3: Computing indicators...")
        df = detector.compute_indicators(df)

        logger.info("Step 3/3: Running partitioned backtest...")

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
                logger.warning(f"{label}: no data")
                results[label] = backtester._empty_result()
                continue

            df_part = detector.detect_signals(df_part)
            result = backtester.run(df_part)
            results[label] = result

            self._print_part_report(label, start, end, result, df_part, config)

            # Print VIX tier distribution
            tier_dist = result.get("vix_tier_distribution", {})
            if tier_dist:
                print(f"\n  VIX Tier Distribution: {tier_dist}")

        self._print_comparison(results)
        self._print_today_signal(df, detector, config)

        return {
            "part_a": results.get("Part A (In-Sample)", backtester._empty_result()),
            "part_b": results.get("Part B (Out-of-Sample)", backtester._empty_result()),
            "part_c": results.get("Part C (Live)", backtester._empty_result()),
        }

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQVixAdaptiveConfig):
            super()._print_strategy_params(config)
            return

        print(f"  Drawdown threshold:  {config.drawdown_threshold:.0%}")
        print(f"  RSI period/thr:      RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  Volume multiplier:   {config.volume_multiplier}x")
        print(f"  Cooldown:            {config.cooldown_days} days")
        print(f"  VIX data source:     {config.vix_ticker}")
        print("  VIX-Adaptive Exit Tiers:")
        for tier in config.vix_tiers:
            vix_range = (
                f"VIX >= {tier.vix_min:.0f}"
                if tier.vix_max >= 999
                else f"VIX {tier.vix_min:.0f}-{tier.vix_max:.0f}"
            )
            print(
                f"    [{tier.label}] {vix_range}: "
                f"TP +{tier.profit_target:.0%} / SL {tier.stop_loss:.0%} / "
                f"{tier.holding_days}d"
            )

"""
TQQQ-015: QQQ Trend Breakout → Trade TQQQ 策略
QQQ BB Squeeze Breakout Strategy (trade TQQQ for 3x amplification)

以 QQQ 波動收縮後的突破訊號進場買入 TQQQ，捕捉 NASDAQ 趨勢啟動的 3 倍放大報酬。
Uses QQQ BB squeeze breakout signals to enter TQQQ, capturing 3x amplified NASDAQ trend moves.
"""

import logging

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_015_qqq_trend_breakout.config import (
    TQQQQqqBreakoutConfig,
    create_default_config,
)
from trading.experiments.tqqq_015_qqq_trend_breakout.signal_detector import (
    TQQQQqqBreakoutDetector,
)

logger = logging.getLogger(__name__)


class TQQQQqqTrendBreakoutStrategy(ExecutionModelStrategy):
    """
    TQQQ-015: QQQ Trend Breakout → Trade TQQQ（含成交模型）

    訊號邏輯: QQQ BB(20,2) 擠壓突破 + QQQ SMA(50) 趨勢確認
    交易標的: TQQQ（3x leveraged NASDAQ）
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQQqqBreakoutDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQQqqBreakoutConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def run(self) -> dict:
        """覆寫 run() 以合併 QQQ 數據供 BB Squeeze 訊號偵測使用。"""
        config = self.create_config()
        detector = self.create_detector()
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80
        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        if not isinstance(config, TQQQQqqBreakoutConfig):
            logger.error("Config type mismatch")
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        logger.info(
            "Step 1/3: Fetching data for %s + %s...",
            config.tickers,
            config.qqq_ticker,
        )
        data = fetcher.fetch_all(config.tickers + [config.qqq_ticker])

        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error("Failed to fetch %s data", primary_ticker)
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]

        # Merge QQQ close price
        if config.qqq_ticker in data:
            qqq_df = data[config.qqq_ticker]
            qqq_close = qqq_df["Close"]
            if hasattr(qqq_close, "columns"):
                qqq_close = qqq_close.iloc[:, 0]
            df["QQQ_Close"] = qqq_close.reindex(df.index, method="ffill")
            logger.info(
                "QQQ close merged, range %.2f ~ %.2f",
                df["QQQ_Close"].min(),
                df["QQQ_Close"].max(),
            )
        else:
            logger.warning("Failed to fetch %s, signals will be empty", config.qqq_ticker)

        print(
            f"  原始資料期間: {df.index[0].strftime('%Y-%m-%d')} ~ "
            f"{df.index[-1].strftime('%Y-%m-%d')}"
        )
        print(f"  原始資料筆數: {len(df)} 個交易日\n")

        logger.info("Step 2/3: Computing indicators and detecting signals...")
        df = detector.compute_indicators(df)

        logger.info("Step 3/3: Running backtests by period...")
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
                logger.warning("%s: no data", label)
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
        if isinstance(config, TQQQQqqBreakoutConfig):
            print("  訊號來源 (Signal source):        QQQ (1x NASDAQ ETF)")
            print("  交易標的 (Trade target):         TQQQ (3x leveraged)")
            print(f"  動量門檻 (Momentum thr):         QQQ ROC(10) > {config.momentum_threshold}%")
            print("  趨勢確認 (Trend): QQQ Close > SMA(50) & SMA(200)")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

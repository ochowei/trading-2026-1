"""
NVDA-016: Sector-Health Confirmed Multi-Week Regime-Aware MBPC Strategy

在 NVDA-013 Att3（Multi-Week Regime-Aware MBPC）基礎上加入 SMH 10 日報酬
作為半導體板塊健康確認閘門。覆寫 run() 以額外抓取 SMH 資料並合併至 NVDA
DataFrame（沿用 IWM-015 / XLU-006 / TLT-009 跨資產取值模式）。
"""

import logging

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_016_sector_confirmed_mbpc.config import (
    NVDA016Config,
    create_default_config,
)
from trading.experiments.nvda_016_sector_confirmed_mbpc.signal_detector import (
    NVDA016SectorConfirmedMBPCDetector,
)

logger = logging.getLogger(__name__)


class NVDA016SectorConfirmedMBPCStrategy(ExecutionModelStrategy):
    """NVDA-016：Sector-Health Confirmed MBPC 策略（含成交模型 + SMH 板塊確認）"""

    slippage_pct: float = 0.0015  # 同 NVDA-013（0.15%，個股滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDA016SectorConfirmedMBPCDetector(create_default_config())

    def run(self) -> dict:
        """覆寫 run() 以抓取 SMH 資料合併至 NVDA DataFrame"""
        config = create_default_config()
        detector = self.create_detector()
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start, max_workers=1)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載 NVDA + SMH 資料
        macro_ticker = config.macro_ticker
        tickers_to_fetch = list(config.tickers) + [macro_ticker]
        logger.info("Step 1/3: 下載數據 (Fetching data for %s)...", tickers_to_fetch)
        data = fetcher.fetch_all(tickers_to_fetch)

        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error("無法取得 %s 數據", primary_ticker)
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]
        print(
            f"  原始資料期間: {df.index[0].strftime('%Y-%m-%d')}"
            f" ~ {df.index[-1].strftime('%Y-%m-%d')}"
        )
        print(f"  原始資料筆數: {len(df)} 個交易日\n")

        # 合併 SMH Close 到 NVDA DataFrame
        if macro_ticker in data:
            macro_df = data[macro_ticker]
            df["SMH_Close"] = macro_df["Close"].reindex(df.index, method="ffill")
            logger.info("%s 資料已合併 (%d 筆)", macro_ticker, df["SMH_Close"].notna().sum())
        else:
            logger.warning("無法取得 %s 數據，sector confirmation 將失效", macro_ticker)

        # Step 2: 計算指標
        logger.info("Step 2/3: 計算指標與偵測訊號 (Computing indicators & detecting signals)...")
        df = detector.compute_indicators(df)

        # Step 3: 分區間回測
        logger.info("Step 3/3: 分區間回測 (Running backtests for each part)...")

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
                logger.warning("%s: 無資料 (no data)", label)
                results[label] = backtester._empty_result()
                continue

            df_part = detector.detect_signals(df_part)
            result = backtester.run(df_part)
            result["backtest_period"] = {"start": start, "end": end}
            results[label] = result

            self._print_part_report(label, start, end, result, df_part, config)

        # 印出比較表
        self._print_comparison(results)

        # 今日訊號檢查
        self._print_today_signal(df, detector, config)

        return {
            "metadata": {"execution_time": pd.Timestamp.now().isoformat()},
            "part_a": results.get("Part A (In-Sample)", backtester._empty_result()),
            "part_b": results.get("Part B (Out-of-Sample)", backtester._empty_result()),
            "part_c": results.get("Part C (Live)", backtester._empty_result()),
        }

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDA016Config):
            print(
                f"  Donchian: {config.donchian_period} 日新高，近 "
                f"{config.breakout_recency_days} 日內 breakout"
            )
            print(f"  趨勢過濾 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            print(
                f"  淺回檔範圍: {config.pullback_max:.1%} ~ {config.pullback_min:.1%}"
                f"（相對近 {config.pullback_lookback} 日高點）"
            )
            print(
                f"  RSI({config.rsi_period}) 中性區: [{config.rsi_min:.0f}, {config.rsi_max:.0f}]"
            )
            print(f"  多頭 K 棒: Close > Open = {config.bullish_close_required}")
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            print(
                f"  板塊健康閘門: {config.macro_ticker}"
                f" {config.macro_lookback} 日報酬 >= {config.macro_min_return:.1%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 個交易日")
        super()._print_strategy_params(config)

"""
XBI-016: Macro-Confirmed Pullback Mean Reversion Strategy

在 XBI-015 Att2（Multi-Week Regime-Aware Pullback MR，全域最優 min(A,B) 0.46）
基礎上加入 broad-market macro context confirmation gate（lesson #25 IWM-015
跨資產假設驗證）。覆寫 run() 以額外抓取 macro proxy（QQQ/SPY）資料並合併至
XBI DataFrame（沿用 IWM-015 / XLU-006 / TLT-009 跨資產取值模式）。
"""

import logging

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_016_macro_confirmed_mr.config import (
    XBI016Config,
    create_default_config,
)
from trading.experiments.xbi_016_macro_confirmed_mr.signal_detector import (
    XBI016SignalDetector,
)

logger = logging.getLogger(__name__)


class XBI016Strategy(ExecutionModelStrategy):
    """XBI-016 Macro-Confirmed Pullback MR（含成交模型 + macro 宏觀確認）"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI016SignalDetector(create_default_config())

    def run(self) -> dict:
        """覆寫 run() 以抓取 macro proxy 資料合併至 XBI DataFrame"""
        config = create_default_config()
        detector = self.create_detector()
        backtester = self.create_backtester(config)
        # 單執行緒抓取以避免 yfinance 多執行緒下載對 auto_adjust 的競爭條件
        fetcher = DataFetcher(start=config.data_start, max_workers=1)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載 XBI + macro proxy 資料
        macro_ticker = config.macro_ticker  # type: ignore[attr-defined]
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

        # 合併 macro proxy Close 到 XBI DataFrame
        if macro_ticker in data:
            macro_df = data[macro_ticker]
            df["MACRO_Close"] = macro_df["Close"].reindex(df.index, method="ffill")
            logger.info("%s 資料已合併 (%d 筆)", macro_ticker, df["MACRO_Close"].notna().sum())
        else:
            logger.warning("無法取得 %s 數據，macro confirmation 將失效", macro_ticker)

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
        if isinstance(config, XBI016Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(f"  反轉K線: ClosePos ≥ {config.close_position_threshold:.0%}")
            if config.use_vol_regime:
                print(
                    f"  波動 regime: ATR({config.atr_regime_short})"
                    f" ≤ {config.vol_regime_max_ratio}"
                    f" × ATR({config.atr_regime_long})"
                )
            else:
                print("  波動 regime: 已停用")
            print(
                f"  宏觀確認閘門: {config.macro_ticker}"
                f" {config.macro_lookback} 日報酬 ≤ {config.macro_max_return:.1%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

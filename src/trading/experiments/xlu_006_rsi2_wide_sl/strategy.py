"""
XLU-006: Pullback + WR + TLT Rate Regime Filter
(XLU 回檔 + WR + TLT 利率環境過濾)

基於 XLU-003 進場條件，加入 TLT 60日 ROC 過濾排除快速升息期訊號。
覆寫 run() 以額外抓取 TLT 資料並合併至 XLU DataFrame。
"""

import logging

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_006_rsi2_wide_sl.config import (
    XLU006Config,
    create_default_config,
)
from trading.experiments.xlu_006_rsi2_wide_sl.signal_detector import (
    XLURSI2WideSLSignalDetector,
)

logger = logging.getLogger(__name__)


class XLURSI2WideSLStrategy(ExecutionModelStrategy):
    """XLU 回檔 + WR + TLT 利率環境過濾 (XLU-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLURSI2WideSLSignalDetector(create_default_config())

    def run(self) -> dict:
        """覆寫 run() 以抓取 TLT 資料合併至 XLU DataFrame"""
        config = create_default_config()
        detector = self.create_detector()
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載 XLU + TLT 資料
        tickers_to_fetch = config.tickers + [config.tlt_ticker]
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

        # 合併 TLT Close 到 XLU DataFrame
        if config.tlt_ticker in data:
            tlt_df = data[config.tlt_ticker]
            df["TLT_Close"] = tlt_df["Close"].reindex(df.index, method="ffill")
            logger.info("TLT 資料已合併 (%d 筆)", df["TLT_Close"].notna().sum())

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
        if isinstance(config, XLU006Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R 期數: {config.wr_period}")
            print(f"  Williams %R 門檻: <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position):"
                f" >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  TLT 利率過濾: TLT {config.tlt_roc_period}日 ROC"
                f" > {config.tlt_roc_threshold:.0%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

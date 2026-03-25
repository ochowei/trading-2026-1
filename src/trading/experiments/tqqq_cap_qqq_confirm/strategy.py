"""
TQQQ QQQ 確認策略 (TQQQ Capitulation QQQ Confirm Strategy)
在原始恐慌抄底訊號基礎上，加入 QQQ RSI(14) < 35 確認底層指數也處於超賣狀態。
Filters capitulation signals to only enter when QQQ RSI < 35.
"""

import logging
import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.data_fetcher import DataFetcher
from trading.experiments.tqqq_cap_qqq_confirm.config import (
    TQQQCapQqqConfirmConfig,
    create_default_config,
)
from trading.experiments.tqqq_cap_qqq_confirm.signal_detector import TQQQCapQqqConfirmDetector

logger = logging.getLogger(__name__)


class TQQQCapQqqConfirmStrategy(BaseStrategy):
    """
    TQQQ QQQ 確認策略
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapQqqConfirmDetector(create_default_config())

    def run(self) -> dict:
        """
        覆寫 run() 以在 fetch 後計算 QQQ RSI 並合併至 TQQQ DataFrame。
        """
        config = create_default_config()
        detector = TQQQCapQqqConfirmDetector(config)
        backtester = self.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 80

        print(f"\n{separator}")
        print(f"  {config.display_name}")
        print(f"{separator}\n")

        # Step 1: 下載 TQQQ 和 QQQ 數據
        logger.info(f"Step 1/3: 下載數據 (Fetching data for {config.tickers} + {config.qqq_ticker})...")
        all_tickers = config.tickers + [config.qqq_ticker]
        data = fetcher.fetch_all(all_tickers)

        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error(f"無法取得 {primary_ticker} 數據")
            empty = backtester._empty_result()
            return {"part_a": empty, "part_b": empty, "part_c": empty}

        df = data[primary_ticker]

        # 計算 QQQ RSI 並合併 (Calculate QQQ RSI and merge onto TQQQ DataFrame)
        if config.qqq_ticker in data:
            qqq_df = data[config.qqq_ticker]
            # 計算 QQQ RSI
            qqq_rsi = detector._compute_rsi(qqq_df["Close"], config.qqq_rsi_period)
            if qqq_rsi is not None:
                df["QQQ_RSI"] = qqq_rsi.reindex(df.index, method="ffill")
                logger.info(
                    f"[QqqConfirm] QQQ RSI({config.qqq_rsi_period}) 資料已合併，"
                    f"範圍 {df['QQQ_RSI'].min():.1f} ~ {df['QQQ_RSI'].max():.1f}"
                )
            else:
                 logger.warning(
                    f"[QqqConfirm] 無法計算 {config.qqq_ticker} RSI 數據，過濾將被跳過"
                )
        else:
            logger.warning(
                f"[QqqConfirm] 無法取得 {config.qqq_ticker} 數據，過濾將被跳過"
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
        if not isinstance(config, TQQQCapQqqConfirmConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  QQQ RSI 週期/閾值:               QQQ RSI({config.qqq_rsi_period}) < {config.qqq_rsi_threshold}")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

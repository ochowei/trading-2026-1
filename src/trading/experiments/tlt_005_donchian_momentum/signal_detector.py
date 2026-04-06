"""
TLT-005 訊號偵測器：Donchian 突�� + 趨勢跟蹤
(TLT-005 Signal Detector: Donchian Channel Breakout + Trend Following)

進場條件（全部滿足）：
1. Close > 過去 N 日最高 High（Donchian ���破，排除當日）
2. Close > SMA(50)（趨勢確認，避免在下跌��勢中買入）
3. 冷卻期 10 個交易日

Entry conditions (all must be met):
1. Close > highest High of past N days (Donchian breakout, excluding today)
2. Close > SMA(50) (trend confirmation, avoids buying in downtrends)
3. 10-day cooldown between signals
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_005_donchian_momentum.config import TLTBreakoutTrendConfig

logger = logging.getLogger(__name__)


class TLTBreakoutTrendSignalDetector(BaseSignalDetector):
    def __init__(self, config: TLTBreakoutTrendConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian Channel: 過去 N 日的最高 High（排除當日）
        n = self.config.donchian_period
        df["Donchian_High"] = df["High"].shift(1).rolling(n).max()

        # SMA 趨勢確認
        df["SMA"] = df["Close"].rolling(self.config.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件 1: 收盤突破 Donchian 上軌（新高突破）
        cond_breakout = df["Close"] > df["Donchian_High"]

        # 條件 2: 收盤高於 SMA（上升趨勢）
        cond_trend = df["Close"] > df["SMA"]

        df["Signal"] = cond_breakout & cond_trend

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False

        signal_count = df["Signal"].sum()
        logger.info("TLT-005: Detected %d Donchian breakout signals", signal_count)
        return df

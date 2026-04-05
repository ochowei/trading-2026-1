"""
DIA-008 訊號偵測器：20-day Pullback Range + Williams %R (Attempt 3)
DIA-008 Signal Detector: 20-day Pullback Range Mean Reversion

進場條件（全部滿足）：
1. 20 日高點回檔 3%-7%（有意義回檔但非崩盤）
2. Williams %R(10) <= -80（超賣確認）
3. ClosePos >= 40%（日內反轉確認）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_008_momentum_pullback.config import (
    DIA008PullbackRangeConfig,
)

logger = logging.getLogger(__name__)


class DIA008MomentumPullbackDetector(BaseSignalDetector):
    """DIA 20-day Pullback Range 訊號偵測器"""

    def __init__(self, config: DIA008PullbackRangeConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 20-day rolling high
        n = self.config.pullback_lookback
        df["High_20d"] = df["High"].rolling(n).max()

        # Pullback from 20-day high
        df["Pullback"] = (df["High_20d"] - df["Close"]) / df["High_20d"]

        # Williams %R(10)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        wr_range = highest - lowest
        df["WR"] = ((highest - df["Close"]) / wr_range) * -100
        df.loc[wr_range == 0, "WR"] = -50.0

        # Close Position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Pullback from 20-day high within 3%-7%
        cond_pb_min = df["Pullback"] >= self.config.pullback_min
        cond_pb_max = df["Pullback"] <= self.config.pullback_max

        # 2. Williams %R oversold
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 3. Close position (reversal candle)
        cond_cp = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pb_min & cond_pb_max & cond_wr & cond_cp

        # Cooldown
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
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
        logger.info("DIA-008: Detected %d pullback range signals", signal_count)
        return df

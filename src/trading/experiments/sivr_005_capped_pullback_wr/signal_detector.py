"""
SIVR 回檔範圍 + Williams %R 訊號偵測器
基於 SIVR-003，新增回檔上限 15% 過濾極端崩盤訊號。

Based on SIVR-003, adds pullback cap at 15% to filter extreme crash signals.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_005_capped_pullback_wr.config import (
    SIVRCappedPullbackWRConfig,
)

logger = logging.getLogger(__name__)


class SIVRCappedPullbackWRSignalDetector(BaseSignalDetector):
    """
    SIVR 回檔範圍 + Williams %R 訊號偵測器

    三條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 ≥ 7%
    2. 收盤價相對 10 日最高價回檔 ≤ 15%（過濾極端崩盤）
    3. Williams %R(10) ≤ -80（超賣）
    """

    def __init__(self, config: SIVRCappedPullbackWRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 三條件同時成立
        df["Signal"] = cond_pullback_min & cond_pullback_cap & cond_wr

        # 冷卻機制
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
            logger.info("SIVR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("SIVR: Detected %d Capped Pullback+WR reversion signals", signal_count)
        return df

"""
URA-002 訊號偵測器：回檔範圍 + Williams %R 均值回歸
(URA-002 Signal Detector: Pullback Range + Williams %R Mean Reversion)

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔（可調範圍）
2. Williams %R(10) ≤ -80（超賣確認）
3. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_002_asymmetric_narrow.config import (
    URAAsymmetricNarrowConfig,
)

logger = logging.getLogger(__name__)


class URAAsymmetricNarrowSignalDetector(BaseSignalDetector):
    """
    URA 回檔範圍 + Williams %R 訊號偵測器

    三條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 ≥ pullback_threshold
    2. 回檔幅度 ≤ pullback_upper（過濾極端崩盤）
    3. Williams %R(10) ≤ -80（超賣）
    """

    def __init__(self, config: URAAsymmetricNarrowConfig):
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
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 三條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_wr

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
            logger.info("URA: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA: Detected %d Pullback+WR reversion signals", signal_count)
        return df

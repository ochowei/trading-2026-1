"""
CIBR 回檔 + Williams %R 訊號偵測器
以「收盤價相對 10 日最高價的回檔幅度」搭配 Williams %R(10) 確認超賣。
回檔幅度天然隨趨勢調整，在強勢行情中仍能偵測到中等回調。

Uses pullback from 10-day high + Williams %R(10) for oversold confirmation.
Pullback adapts naturally to trend, catching moderate dips in strong uptrends.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_001_pullback_wr.config import CIBRPullbackWRConfig

logger = logging.getLogger(__name__)


class CIBRPullbackWRSignalDetector(BaseSignalDetector):
    """
    CIBR 回檔 + Williams %R 訊號偵測器

    雙條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 >= 5%
    2. Williams %R(10) <= -80（超賣）
    """

    def __init__(self, config: CIBRPullbackWRConfig):
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

        # 條件一：回檔幅度
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 雙條件同時成立
        df["Signal"] = cond_pullback & cond_wr

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
            logger.info("CIBR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR: Detected %d Pullback+WR reversion signals", signal_count)
        return df

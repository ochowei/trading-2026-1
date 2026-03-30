"""
IBIT-002 訊號偵測器：回檔 + Williams %R 均值回歸（出場優化）
(IBIT-002 Signal Detector: Pullback + Williams %R with Exit Optimization)

進場條件（同 IBIT-001，全部滿足）：
1. 收盤價相對 10 日最高價回檔 12-22%
2. Williams %R(10) <= -80
3. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ibit_002_rsi2_pullback.config import IBITRSI2PullbackConfig

logger = logging.getLogger(__name__)


class IBITRSI2PullbackSignalDetector(BaseSignalDetector):
    """IBIT 回檔 + WR 訊號偵測器（出場優化版）"""

    def __init__(self, config: IBITRSI2PullbackConfig):
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

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold

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
            logger.info("IBIT-002: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("IBIT-002: Detected %d Pullback+WR signals", signal_count)
        return df

"""
GLD 回檔 + Williams %R 訊號偵測器
以「收盤價相對 10 日最高價的回檔幅度」取代 Keltner Channel 下軌。
回檔幅度天然隨趨勢調整，在強勢行情中仍能偵測到中等回調。
搭配 Williams %R(10) 確認短期超賣。

Uses pullback from 10-day high instead of Keltner Channel lower band.
Pullback adapts naturally to trend, catching moderate dips in strong uptrends.
Williams %R(10) confirms short-term oversold condition.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_006_pullback_wr.config import GLDPullbackWRConfig

logger = logging.getLogger(__name__)


class GLDPullbackWRSignalDetector(BaseSignalDetector):
    def __init__(self, config: GLDPullbackWRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = cond_pullback & cond_wr

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
        logger.info("GLD: Detected %d Pullback+WR reversion signals", signal_count)
        return df

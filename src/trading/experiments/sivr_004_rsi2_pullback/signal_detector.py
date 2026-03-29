"""
SIVR RSI(2) + 回檔範圍訊號偵測器
以 RSI(2) 取代 WR(10) 作為超賣確認，搭配回檔範圍 7-15% 和 2 日跌幅過濾。

Uses RSI(2) instead of WR(10) for oversold confirmation, with capped pullback range
7-15% and 2-day decline filter for momentum confirmation.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_004_rsi2_pullback.config import SIVRRSI2PullbackConfig

logger = logging.getLogger(__name__)


class SIVRRSI2PullbackSignalDetector(BaseSignalDetector):
    """
    SIVR RSI(2) + 回檔範圍訊號偵測器

    三重條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 7-15%
    2. RSI(2) < 15（極端短期超賣）
    3. 2 日跌幅 ≥ 3%（短期動量確認）
    """

    def __init__(self, config: SIVRRSI2PullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(
            com=self.config.rsi_period - 1, min_periods=self.config.rsi_period
        ).mean()
        avg_loss = loss.ewm(
            com=self.config.rsi_period - 1, min_periods=self.config.rsi_period
        ).mean()
        rs = avg_gain / avg_loss
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日跌幅
        df["Decline_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度 7-15%
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap

        # 條件二：RSI(2) 超賣
        cond_rsi = df["RSI2"] < self.config.rsi_threshold

        # 條件三：2 日跌幅（threshold=0 表示停用）
        if self.config.decline_2d_threshold < 0:
            cond_decline = df["Decline_2d"] <= self.config.decline_2d_threshold
            df["Signal"] = cond_pullback & cond_cap & cond_rsi & cond_decline
        else:
            df["Signal"] = cond_pullback & cond_cap & cond_rsi

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
        logger.info("SIVR: Detected %d RSI(2)+Pullback reversion signals", signal_count)
        return df

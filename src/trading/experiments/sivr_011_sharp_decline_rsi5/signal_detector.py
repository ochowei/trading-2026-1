"""
SIVR 急跌 + RSI(5) 訊號偵測器
改用 RSI(5) 取代 WR(10)，並加入 2 日跌幅過濾。

Uses RSI(5) instead of WR(10), plus 2-day decline filter.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_011_sharp_decline_rsi5.config import (
    SIVRSharpDeclineRSI5Config,
)

logger = logging.getLogger(__name__)


class SIVRSharpDeclineRSI5SignalDetector(BaseSignalDetector):
    """
    SIVR 急跌 + RSI(5) 訊號偵測器

    四條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 ≥ 7%
    2. 收盤價相對 10 日最高價回檔 ≤ 15%（過濾極端崩盤）
    3. RSI(5) < 30（短期動能耗竭）
    4. 2 日跌幅 ≥ 3.5%（急速殺跌確認）
    """

    def __init__(self, config: SIVRSharpDeclineRSI5Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(5)
        rsi_n = self.config.rsi_period
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.rolling(rsi_n).mean()
        avg_loss = loss.rolling(rsi_n).mean()
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        df["RSI"] = 100 - (100 / (1 + rs))

        # 2 日跌幅
        decline_n = self.config.decline_days
        df["Decline_2d"] = df["Close"].pct_change(decline_n)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap

        # 條件三：RSI(5) 超賣
        cond_rsi = df["RSI"] < self.config.rsi_threshold

        # 條件四：2 日急跌
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold

        # 四條件同時成立
        df["Signal"] = cond_pullback_min & cond_pullback_cap & cond_rsi & cond_decline

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
        logger.info("SIVR: Detected %d Sharp Decline+RSI(5) reversion signals", signal_count)
        return df

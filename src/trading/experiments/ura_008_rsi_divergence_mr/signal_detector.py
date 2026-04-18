"""
URA RSI Bullish Divergence + URA-004 訊號偵測器 (URA-008)

五條件同時成立時觸發訊號：
1. 收盤價相對 10 日最高價回檔 ≥ 10%
2. 收盤價相對 10 日最高價回檔 ≤ 20%（過濾極端崩盤）
3. RSI(2) < 15（短週期超賣）
4. 2 日跌幅 ≤ -3%（近期恐慌）
5. RSI(14) bullish hook：RSI 自過去 N 日最低點回升 ≥ H 點，且該最低點 ≤ 35
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_008_rsi_divergence_mr.config import (
    URARSIDivergenceMRConfig,
)

logger = logging.getLogger(__name__)


class URARSIDivergenceMRSignalDetector(BaseSignalDetector):
    """URA RSI Bullish Divergence + Pullback + RSI(2) + 2DD 訊號偵測器"""

    def __init__(self, config: URARSIDivergenceMRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)

        rsi2_period = self.config.rsi2_period
        avg_gain_2 = gain.ewm(alpha=1 / rsi2_period, min_periods=rsi2_period, adjust=False).mean()
        avg_loss_2 = loss.ewm(alpha=1 / rsi2_period, min_periods=rsi2_period, adjust=False).mean()
        rs_2 = avg_gain_2 / avg_loss_2.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs_2))

        df["TwoDayDecline"] = df["Close"].pct_change(2)

        rsi_period = self.config.rsi_period
        avg_gain_n = gain.rolling(rsi_period).mean()
        avg_loss_n = loss.rolling(rsi_period).mean()
        rs_n = avg_gain_n / avg_loss_n.replace(0, np.nan)
        df["RSI"] = 100 - (100 / (1 + rs_n))

        hook_n = self.config.rsi_hook_lookback
        df["RSI_Min_N"] = df["RSI"].rolling(hook_n).min()
        df["RSI_Hook_Delta"] = df["RSI"] - df["RSI_Min_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_upper
        cond_rsi2 = df["RSI2"] < self.config.rsi2_threshold
        cond_decline = df["TwoDayDecline"] <= self.config.two_day_decline
        cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
        cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_cap
            & cond_rsi2
            & cond_decline
            & cond_hook_delta
            & cond_hook_oversold
        )

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
            logger.info("URA-008: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA-008: Detected %d RSI-Divergence Pullback+RSI(2)+2DD signals", signal_count)
        return df

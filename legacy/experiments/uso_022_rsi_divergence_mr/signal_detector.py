"""
USO RSI(14) Bullish Hook Divergence + Pullback+WR 訊號偵測器 (USO-022 Att3)

進場條件（直接移植 SIVR-015 Att1 結構到 USO）：
1. 10日高點回檔 ≥ 7%
2. 10日高點回檔 ≤ 12%（過濾極端崩盤，USO-013 硬上限）
3. Williams %R(10) ≤ -80（超賣）
4. RSI(14) bullish hook：RSI 自過去 5 日最低點回升 ≥ 3 點，且該最低點 ≤ 35
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_022_rsi_divergence_mr.config import (
    USORSIDivergenceMRConfig,
)

logger = logging.getLogger(__name__)


class USORSIDivergenceMRSignalDetector(BaseSignalDetector):
    """USO RSI(14) Bullish Hook Divergence + Pullback+WR 訊號偵測器"""

    def __init__(self, config: USORSIDivergenceMRConfig):
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

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)

        rsi14_n = self.config.rsi14_period
        avg_gain14 = gain.rolling(rsi14_n).mean()
        avg_loss14 = loss.rolling(rsi14_n).mean()
        rs14 = avg_gain14 / avg_loss14.replace(0, np.nan)
        df["RSI14"] = 100 - (100 / (1 + rs14))

        hook_n = self.config.rsi_hook_lookback
        df["RSI14_Min_N"] = df["RSI14"].rolling(hook_n).min()
        df["RSI14_Hook_Delta"] = df["RSI14"] - df["RSI14_Min_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_hook_delta = df["RSI14_Hook_Delta"] >= self.config.rsi_hook_delta
        cond_hook_oversold = df["RSI14_Min_N"] <= self.config.rsi_hook_max_min

        df["Signal"] = (
            cond_pullback & cond_not_crash & cond_wr & cond_hook_delta & cond_hook_oversold
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
            logger.info("USO-022: %d signals suppressed by cooldown", len(suppressed))

        logger.info("USO-022: Detected %d signals", df["Signal"].sum())
        return df

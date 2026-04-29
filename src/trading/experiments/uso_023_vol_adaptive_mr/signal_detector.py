"""
USO-023 訊號偵測器：波動率自適應 RSI(2) 均值回歸

進場條件（全部滿足）：
1. 10 日高點回檔 7-12%（同 USO-013）
2. RSI(2) < 15（同 USO-013）
3. 2 日報酬 ≤ -2.5%（同 USO-013）
4. ATR(5) / ATR(20) > 1.05（新增：波動率飆升，過濾慢磨下跌）
5. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_023_vol_adaptive_mr.config import USO023Config

logger = logging.getLogger(__name__)


class USO023SignalDetector(BaseSignalDetector):
    """USO-023 波動率自適應均值回歸訊號偵測器"""

    def __init__(self, config: USO023Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（同 USO-013）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)（同 USO-013）
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日報酬（同 USO-013）
        df["Return_2d"] = df["Close"].pct_change(2)

        # ATR ratio: short-term vs long-term volatility（USO-023 新增）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold
        cond_drop_cap = df["Return_2d"] >= self.config.drop_2d_cap
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        df["Signal"] = (
            cond_pullback & cond_not_crash & cond_rsi & cond_drop & cond_drop_cap & cond_vol
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
            logger.info("USO-023: %d signals suppressed by cooldown", len(suppressed))

        logger.info("USO-023: Detected %d signals", df["Signal"].sum())
        return df

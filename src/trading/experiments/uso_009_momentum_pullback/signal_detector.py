"""
USO 回檔 + RSI(2) + 2日急跌訊號偵測器 (USO-009)
進場：10 日高點回檔 ≥ 6% + RSI(2) < 15 + 2日報酬 ≤ -2.5%。
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_009_momentum_pullback.config import USOMomentumPullbackConfig

logger = logging.getLogger(__name__)


class USOMomentumPullbackSignalDetector(BaseSignalDetector):
    """USO 回檔 + RSI(2) + 2日急跌訊號偵測器"""

    def __init__(self, config: USOMomentumPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2) 計算
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2日報酬
        df["Return_2d"] = df["Close"].pct_change(2)
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold
        df["Signal"] = cond_pullback & cond_rsi & cond_drop

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
            logger.info("USO-009: %d signals suppressed by cooldown", len(suppressed))

        logger.info("USO-009: Detected %d signals", df["Signal"].sum())
        return df

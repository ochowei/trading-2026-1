"""
GLD 布林帶均值回歸訊號偵測器
以布林帶下軌取代固定 SMA 乖離閾值，動態適應不同波動度環境。
RSI 放寬至 35 增加訊號頻率，由布林帶過濾品質。

Uses Bollinger Band lower band instead of fixed SMA deviation threshold.
RSI relaxed to 35 for more signals; Bollinger Band filters quality.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_004_bollinger_reversion.config import (
    GLDBollingerReversionConfig,
)

logger = logging.getLogger(__name__)


class GLDBollingerReversionSignalDetector(BaseSignalDetector):
    def __init__(self, config: GLDBollingerReversionConfig):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)
        df["BB_Mid"] = df["Close"].rolling(window=self.config.bb_period).mean()
        bb_std = df["Close"].rolling(window=self.config.bb_period).std()
        df["BB_Lower"] = df["BB_Mid"] - self.config.bb_std * bb_std
        df["BB_Upper"] = df["BB_Mid"] + self.config.bb_std * bb_std
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_bb = df["Close"] < df["BB_Lower"]

        df["Signal"] = cond_rsi & cond_bb

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
        logger.info("GLD: Detected %d Bollinger Band mean reversion signals", signal_count)
        return df

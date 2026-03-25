"""
GLD 追蹤停損均值回歸訊號偵測器
完全複用 GLD-001 的 RSI + SMA 乖離訊號，改善點在出場端（追蹤停損）。
Reuses GLD-001's signal logic. Improvement is on the exit side (trailing stop).
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_trailing_stop.config import GLDTrailingStopConfig

logger = logging.getLogger(__name__)


class GLDTrailingStopSignalDetector(BaseSignalDetector):
    def __init__(self, config: GLDTrailingStopConfig):
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
        df["RSI14"] = self._compute_rsi(df["Close"], self.config.rsi_period)
        df["SMA50"] = df["Close"].rolling(window=self.config.sma_period).mean()
        df["SMA_Deviation"] = (df["Close"] - df["SMA50"]) / df["SMA50"]
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI14"] < self.config.rsi_threshold
        cond_sma_dev = df["SMA_Deviation"] <= self.config.sma_deviation_threshold

        df["Signal"] = cond_rsi & cond_sma_dev

        # Cooldown mechanism (same as GLD-001)
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
        logger.info(f"GLD: Detected {signal_count} mean reversion signals (trailing stop exit)")
        return df

"""
VGK-006 signal detector: Trend Pullback Momentum (Att1)

Entry conditions (all must be met):
1. SMA(20) > SMA(50) — medium-term uptrend confirmed
2. Close > SMA(50) — price above long-term trend
3. 10-day high pullback >= 2% and <= 5% — mild dip in uptrend
4. Close Position >= 40% — intraday reversal confirmation
5. Cooldown 7 trading days
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.vgk_006_trend_pullback_momentum.config import VGK006Config

logger = logging.getLogger(__name__)


class VGK006SignalDetector(BaseSignalDetector):
    def __init__(self, config: VGK006Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Simple Moving Averages for trend detection
        df["SMA_Short"] = df["Close"].rolling(self.config.sma_short_period).mean()
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        # 10-day high pullback
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Close position (intraday reversal)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Trend conditions
        cond_trend = df["SMA_Short"] > df["SMA_Long"]
        cond_above_sma = df["Close"] > df["SMA_Long"]

        # Pullback conditions (shallow: 2-5%)
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap

        # Reversal confirmation
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_trend & cond_above_sma & cond_pullback & cond_cap & cond_reversal

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
        logger.info("VGK-006: Detected %d trend pullback signals", signal_count)
        return df

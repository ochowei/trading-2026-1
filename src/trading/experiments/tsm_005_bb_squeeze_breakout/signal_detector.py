"""
TSM-005 Signal Detector: Bollinger Band Squeeze Breakout

Entry conditions (ALL must be satisfied):
1. BB Width fell below 60-day 25th percentile in past 5 days (volatility contraction)
2. Close > Upper BB(20,2) (breakout above upper band)
3. Close > SMA(50) (uptrend confirmation)
4. 15-day cooldown
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_005_bb_squeeze_breakout.config import TSMBBSqueezeConfig

logger = logging.getLogger(__name__)


class TSMBBSqueezeDetector(BaseSignalDetector):
    """TSM BB Squeeze Breakout Signal Detector"""

    def __init__(self, config: TSMBBSqueezeConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # BB Width percentile rank over window
        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        # Recent squeeze: was there a squeeze in the last N days?
        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Recent squeeze in past 5 days
        cond_squeeze = df["Recent_Squeeze"]

        # Breakout: close above upper band
        cond_breakout = df["Close"] > df["BB_Upper"]

        # Uptrend: close above SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend

        # Cooldown mechanism
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

        signal_count = df["Signal"].sum()
        logger.info("TSM: Detected %d BB squeeze breakout signals", signal_count)
        return df

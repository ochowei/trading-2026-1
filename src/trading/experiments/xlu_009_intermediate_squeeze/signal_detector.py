"""
XLU-009 訊號偵測器：Intermediate BB Squeeze Breakout
XLU-009 Signal Detector: Intermediate BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 25th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20,2.25)（突破上軌，介於 2.0 和 2.5 之間）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_009_intermediate_squeeze.config import XLU009Config

logger = logging.getLogger(__name__)


class XLU009Detector(BaseSignalDetector):
    """XLU Intermediate BB Squeeze Breakout 訊號偵測器"""

    def __init__(self, config: XLU009Config):
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
        logger.info("XLU-009: Detected %d intermediate BB squeeze breakout signals", signal_count)
        return df

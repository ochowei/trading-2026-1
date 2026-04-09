"""
XLU-009 訊號偵測器：Keltner Channel Squeeze Breakout
XLU-009 Signal Detector: KC Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 KC Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper KC（突破上軌，KC mult 2.5）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_009_kc_squeeze_breakout.config import XLU009KCSqueezeConfig

logger = logging.getLogger(__name__)


class XLU009KCSqueezeDetector(BaseSignalDetector):
    """XLU KC Squeeze Breakout 訊號偵測器"""

    def __init__(self, config: XLU009KCSqueezeConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Keltner Channel: EMA ± multiplier × ATR
        ema_period = self.config.ema_period
        atr_period = self.config.atr_period
        mult = self.config.kc_multiplier

        df["KC_Mid"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

        # ATR calculation
        high_low = df["High"] - df["Low"]
        high_prev_close = (df["High"] - df["Close"].shift(1)).abs()
        low_prev_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
        df["ATR"] = true_range.rolling(atr_period).mean()

        df["KC_Upper"] = df["KC_Mid"] + mult * df["ATR"]
        df["KC_Lower"] = df["KC_Mid"] - mult * df["ATR"]
        df["KC_Width"] = (df["KC_Upper"] - df["KC_Lower"]) / df["KC_Mid"]

        # KC Width percentile rank over window
        pct_window = self.config.kc_squeeze_percentile_window
        df["KC_Width_Pct"] = (
            df["KC_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.kc_squeeze_percentile),
                raw=False,
            )
        )

        # Recent squeeze: was there a squeeze in the last N days?
        recent = self.config.kc_squeeze_recent_days
        df["Recent_Squeeze"] = df["KC_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Recent squeeze in past 5 days
        cond_squeeze = df["Recent_Squeeze"]

        # Breakout: close above upper KC band
        cond_breakout = df["Close"] > df["KC_Upper"]

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
        logger.info("XLU-009: Detected %d KC squeeze breakout signals", signal_count)
        return df

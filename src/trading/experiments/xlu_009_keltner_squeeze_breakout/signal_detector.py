"""
XLU-009 訊號偵測器：Keltner Channel Squeeze Breakout
XLU-009 Signal Detector: Keltner Channel Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內曾處於 Squeeze 狀態（BB 上軌 < KC 上軌 且 BB 下軌 > KC 下軌）
2. 收盤價 > KC 上軌（突破 Keltner 上軌，ATR-based）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_009_keltner_squeeze_breakout.config import (
    XLU009KeltnerSqueezeConfig,
)

logger = logging.getLogger(__name__)


class XLU009KeltnerSqueezeDetector(BaseSignalDetector):
    """XLU Keltner Channel Squeeze Breakout 訊號偵測器"""

    def __init__(self, config: XLU009KeltnerSqueezeConfig):
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

        # Keltner Channel (EMA + ATR)
        kc_ema = self.config.kc_ema_period
        kc_atr = self.config.kc_atr_period
        kc_mult = self.config.kc_multiplier

        df["KC_Mid"] = df["Close"].ewm(span=kc_ema, adjust=False).mean()

        # ATR calculation
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["ATR"] = true_range.rolling(kc_atr).mean()

        df["KC_Upper"] = df["KC_Mid"] + kc_mult * df["ATR"]
        df["KC_Lower"] = df["KC_Mid"] - kc_mult * df["ATR"]

        # Squeeze detection: BB bands inside KC bands
        df["Squeeze_On"] = (df["BB_Upper"] < df["KC_Upper"]) & (df["BB_Lower"] > df["KC_Lower"])

        # Recent squeeze: was there a squeeze in the last N days?
        recent = self.config.squeeze_recent_days
        df["Recent_Squeeze"] = df["Squeeze_On"].rolling(recent, min_periods=1).max().astype(bool)

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Recent squeeze in past 5 days
        cond_squeeze = df["Recent_Squeeze"]

        # Breakout: close above Keltner upper band
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
        logger.info("XLU-009: Detected %d Keltner squeeze breakout signals", signal_count)
        return df

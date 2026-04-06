"""
TSLA-007 訊號偵測器：Keltner Channel Breakout
TSLA-007 Signal Detector: Keltner Channel Breakout

進場條件（全部滿足）：
1. 過去 5 日內 KC Width 曾低於 60 日 25th 百分位（近期波動收縮）
2. 收盤價 > Upper KC（突破上軌）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 15 個交易日

Keltner Channel 與 BB 的關鍵差異：
- BB 使用收盤價標準差 → 對單一大K線敏感
- KC 使用 ATR（True Range 均值）→ 含缺口，更穩健
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_007_keltner_breakout.config import TSLAKeltnerConfig

logger = logging.getLogger(__name__)


class TSLAKeltnerDetector(BaseSignalDetector):
    """TSLA Keltner Channel Breakout 訊號偵測器"""

    def __init__(self, config: TSLAKeltnerConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # EMA for Keltner Channel midline
        df["KC_Mid"] = df["Close"].ewm(span=self.config.ema_period, adjust=False).mean()

        # ATR (True Range)
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["ATR"] = true_range.rolling(self.config.atr_period).mean()

        # Keltner Channel
        mult = self.config.atr_multiplier
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

        # Breakout: close above upper Keltner channel
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
        logger.info("TSLA: Detected %d Keltner channel breakout signals", signal_count)
        return df

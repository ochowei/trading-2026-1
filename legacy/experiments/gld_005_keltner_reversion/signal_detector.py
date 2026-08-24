"""
GLD Keltner 通道均值回歸訊號偵測器
以 Keltner Channel 下軌（EMA(20) - 1.5 * ATR(14)）取代布林帶下軌。
ATR 基於真實波幅（含高低價），比標準差更穩健地衡量波動度。
1.5 倍 ATR 為較窄通道，在溫和回調時也能觸發，提高訊號頻率。

Uses Keltner Channel lower band (EMA - 1.5 * ATR) instead of Bollinger Band.
ATR is more robust than standard deviation for measuring volatility.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_005_keltner_reversion.config import GLDKeltnerConfig

logger = logging.getLogger(__name__)


class GLDKeltnerSignalDetector(BaseSignalDetector):
    def __init__(self, config: GLDKeltnerConfig):
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

    @staticmethod
    def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.ewm(span=period, min_periods=period, adjust=False).mean()

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)
        df["EMA"] = df["Close"].ewm(span=self.config.ema_period, adjust=False).mean()
        df["ATR"] = self._compute_atr(df, self.config.atr_period)
        df["Keltner_Lower"] = df["EMA"] - self.config.keltner_multiplier * df["ATR"]
        df["Keltner_Upper"] = df["EMA"] + self.config.keltner_multiplier * df["ATR"]
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_keltner = df["Close"] < df["Keltner_Lower"]

        df["Signal"] = cond_rsi & cond_keltner

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
        logger.info("GLD: Detected %d Keltner Channel reversion signals", signal_count)
        return df

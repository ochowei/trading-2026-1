"""
TSLA-006 訊號偵測器：Donchian Channel Breakout
TSLA-006 Signal Detector: Donchian Channel Breakout

進場條件（全部滿足）：
1. 過去 5 日內 ATR(14) 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > 20 日最高價（突破 Donchian 上軌）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 15 個交易日

Att3: 從 Trend Pullback 改為 Donchian Channel Breakout + ATR 收縮。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_006_trend_pullback.config import TSLATrendPullbackConfig

logger = logging.getLogger(__name__)


class TSLATrendPullbackDetector(BaseSignalDetector):
    """TSLA Donchian Channel Breakout 訊號偵測器"""

    def __init__(self, config: TSLATrendPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian Channel upper band (N-day high, excluding today)
        df["Donchian_Upper"] = df["High"].shift(1).rolling(self.config.donchian_period).max()

        # ATR
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["ATR"] = true_range.rolling(self.config.atr_period).mean()

        # ATR percentile: is ATR low relative to recent history?
        pct_window = self.config.atr_percentile_window
        df["ATR_Low"] = (
            df["ATR"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.atr_percentile),
                raw=False,
            )
        )

        # Recent low ATR: was there a low-ATR day in the last N days?
        recent = self.config.atr_recent_days
        df["Recent_Low_ATR"] = df["ATR_Low"].rolling(recent, min_periods=1).max() >= 1.0

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Recent ATR contraction
        cond_atr_low = df["Recent_Low_ATR"]

        # Breakout: close above Donchian upper channel
        cond_breakout = df["Close"] > df["Donchian_Upper"]

        # Uptrend: close above SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_atr_low & cond_breakout & cond_trend

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
        logger.info("TSLA: Detected %d Donchian breakout signals", signal_count)
        return df

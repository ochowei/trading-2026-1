"""
GLD-011 訊號偵測器：Donchian Channel Breakout
GLD-011 Signal Detector: Donchian Channel Breakout

進場條件（全部滿足）：
1. Close > 30日 Donchian 高點（創 30日新高）
2. Close > SMA(50)（趨勢向上）
3. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_011_donchian_breakout.config import GLD011Config

logger = logging.getLogger(__name__)


class GLD011SignalDetector(BaseSignalDetector):
    """GLD Donchian Channel Breakout 訊號偵測器"""

    def __init__(self, config: GLD011Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian Channel high (excluding current bar)
        n = self.config.donchian_period
        df["Donchian_High"] = df["High"].shift(1).rolling(n).max()

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Breakout: close above Donchian high (new 30-day high)
        cond_breakout = df["Close"] > df["Donchian_High"]

        # Uptrend: close above SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_breakout & cond_trend

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
        logger.info("GLD-011: Detected %d Donchian breakout signals", signal_count)
        return df

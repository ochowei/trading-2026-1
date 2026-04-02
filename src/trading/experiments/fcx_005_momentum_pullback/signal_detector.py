"""
FCX-005 訊號偵測器：RSI(2) 短期極端超賣均值回歸
FCX-005 Signal Detector: RSI(2) Short-Term Extreme Oversold

進場條件（全部滿足）：
1. RSI(2) < 10（極端短期超賣）
2. 2 日跌幅 >= 4%（顯著短期下跌，按 FCX 波動度縮放）
3. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_005_momentum_pullback.config import FCXRSI2Config

logger = logging.getLogger(__name__)


class FCXRSI2Detector(BaseSignalDetector):
    """FCX RSI(2) 短期均值回歸訊號偵測器"""

    def __init__(self, config: FCXRSI2Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)
        period = self.config.rsi_period
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100.0 - (100.0 / (1.0 + rs))

        # N-day decline
        decline_days = self.config.decline_days
        df["Decline"] = df["Close"].pct_change(decline_days)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Extreme short-term oversold
        cond_rsi = df["RSI"] < self.config.rsi_threshold

        # Significant short-term decline
        cond_decline = df["Decline"] <= self.config.decline_threshold

        df["Signal"] = cond_rsi & cond_decline

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
        logger.info("FCX: Detected %d RSI(2) signals", signal_count)
        return df

"""
EEM-005 訊號偵測器：BB 擠壓突破

進場條件（全部滿足）：
1. 近 5 日內 BB 帶寬處於 60 日的 30th 百分位以下（波動率壓縮）
2. 收盤價 > 布林帶上軌（向上突破）
3. 收盤價 > SMA(50)（趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_005_bb_squeeze_breakout.config import EEM005Config

logger = logging.getLogger(__name__)


class EEM005SignalDetector(BaseSignalDetector):
    def __init__(self, config: EEM005Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        df["BB_Mid"] = df["Close"].rolling(self.config.bb_period).mean()
        bb_std = df["Close"].rolling(self.config.bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + self.config.bb_std * bb_std
        df["BB_Lower"] = df["BB_Mid"] - self.config.bb_std * bb_std

        # BB Width (normalized bandwidth)
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # BB Width percentile over lookback window
        window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(window)
            .apply(
                lambda x: np.sum(x <= x.iloc[-1]) / len(x),
                raw=False,
            )
        )

        # Recent squeeze: was BB_Width_Pct below threshold in past N days?
        squeeze_threshold = self.config.bb_squeeze_percentile
        recent = self.config.bb_squeeze_recent_days
        is_squeezed = df["BB_Width_Pct"] <= squeeze_threshold
        df["Recent_Squeeze"] = is_squeezed.rolling(recent).max().fillna(0).astype(bool)

        # Trend confirmation
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend

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
        logger.info("EEM-005: Detected %d BB squeeze breakout signals", signal_count)
        return df

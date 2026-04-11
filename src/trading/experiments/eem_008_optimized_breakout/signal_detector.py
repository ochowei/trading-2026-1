"""
EEM-008 訊號偵測器：優化突破

Att3 進場條件（BB Squeeze + 環境波動率過濾）：
1. 近 5 日內 BB 帶寬處於 60 日的 30th 百分位以下（波動率壓縮）
2. 收盤價 > 布林帶上軌（向上突破）
3. 收盤價 > SMA(50)（趨勢確認）
4. 20 日實現波動率 ≤ 1.4%（環境波動率低，非 EM 危機期）
5. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_008_optimized_breakout.config import EEM008Config

logger = logging.getLogger(__name__)


class EEM008SignalDetector(BaseSignalDetector):
    def __init__(self, config: EEM008Config):
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

        # Realized volatility (ambient vol filter)
        daily_returns = df["Close"].pct_change()
        df["Realized_Vol"] = daily_returns.rolling(self.config.realized_vol_period).std()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_low_vol = df["Realized_Vol"] <= self.config.realized_vol_threshold

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend & cond_low_vol

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
        logger.info("EEM-008: Detected %d vol-filtered breakout signals", signal_count)
        return df

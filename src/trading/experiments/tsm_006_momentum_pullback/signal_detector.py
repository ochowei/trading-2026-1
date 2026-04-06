"""
TSM-006 訊號偵測器：Momentum Pullback
TSM-006 Signal Detector: Momentum Pullback

Attempt 3 最佳版本
進場條件（全部滿足）：
1. 20日 ROC >= 10%（適中動量門檻）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_006_momentum_pullback.config import (
    TSMMomentumPullbackConfig,
)

logger = logging.getLogger(__name__)


class TSMMomentumPullbackDetector(BaseSignalDetector):
    """TSM Momentum Pullback 訊號偵測器"""

    def __init__(self, config: TSMMomentumPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # 20-day ROC (Rate of Change)
        df["ROC_20"] = df["Close"].pct_change(self.config.roc_period)

        # 5-day high and short-term pullback
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Strong recent momentum
        cond_momentum = df["ROC_20"] >= self.config.roc_min

        # Short-term pullback in range [min, max]
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )

        # Uptrend: close above SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_momentum & cond_pullback & cond_trend

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
        logger.info("TSM: Detected %d momentum pullback signals", signal_count)
        return df

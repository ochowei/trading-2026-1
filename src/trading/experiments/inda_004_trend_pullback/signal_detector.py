"""
INDA-004 訊號偵測器：趨勢回調買入

進場條件（全部滿足）：
1. Close > SMA(50) 且 SMA(50) 上升中（上升趨勢確認 + 斜率過濾）
2. 10 日高點回撤 >= 3% 且 <= 7%
3. WR(10) <= -80（短期超賣確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_004_trend_pullback.config import (
    INDATrendPullbackConfig,
)

logger = logging.getLogger(__name__)


class INDATrendPullbackDetector(BaseSignalDetector):
    def __init__(self, config: INDATrendPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # SMA trend + slope
        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()
        df["SMA_Slope"] = df["SMA_Trend"] - df["SMA_Trend"].shift(cfg.sma_slope_lookback)

        # 10-day high pullback
        n = cfg.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = cfg.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Uptrend: price above rising SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_slope = df["SMA_Slope"] > 0

        # Pullback within range
        cond_pullback = df["Pullback"] <= cfg.pullback_threshold
        cond_cap = df["Pullback"] >= cfg.pullback_cap

        # Oversold within uptrend
        cond_wr = df["WR"] <= cfg.wr_threshold

        df["Signal"] = cond_trend & cond_slope & cond_pullback & cond_cap & cond_wr

        # Cooldown
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False

        signal_count = df["Signal"].sum()
        logger.info("INDA-004: Detected %d trend pullback signals", signal_count)
        return df

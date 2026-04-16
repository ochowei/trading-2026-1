"""
CIBR 趨勢動量回調訊號偵測器 (CIBR Trend Momentum Pullback Signal Detector)

三條件同時成立時觸發訊號：
1. Close > SMA(50) — 確認上升趨勢
2. Close vs 5日最高 High 回調 ≥ 2.5% — 短期回調（1.6σ）
3. WR(5) ≤ -70 — 短期超賣確認
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_007_trend_momentum_pullback.config import (
    CIBRTrendMomentumConfig,
)

logger = logging.getLogger(__name__)


class CIBRTrendMomentumSignalDetector(BaseSignalDetector):
    """CIBR 趨勢動量回調訊號偵測器"""

    def __init__(self, config: CIBRTrendMomentumConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA(50) 趨勢線
        df["SMA50"] = df["Close"].rolling(self.config.sma_period).mean()

        # 回調幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R (短週期)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：趨勢確認（收盤 > SMA50）
        cond_trend = df["Close"] > df["SMA50"]

        # 條件二：短期回調
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件三：短期超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 三條件同時成立
        df["Signal"] = cond_trend & cond_pullback & cond_wr

        # 冷卻機制
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
            logger.info("CIBR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR: Detected %d Trend Momentum Pullback signals", signal_count)
        return df

"""
DIA-010 訊號偵測器：RSI(5) 趨勢回調
(DIA-010 Signal Detector: RSI(5) Trend Pullback)

進場條件（全部滿足）：
1. 收盤 > SMA(50)（確認上升趨勢）
2. RSI(5) < 30（短期超賣回調）
3. 3 日累計跌幅 >= 2%（確認回調幅度）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_010_rsi5_trend_pullback.config import (
    DIARsi5TrendPullbackConfig,
)

logger = logging.getLogger(__name__)


class DIARsi5TrendPullbackSignalDetector(BaseSignalDetector):
    def __init__(self, config: DIARsi5TrendPullbackConfig):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA(50) 趨勢線
        df["SMA_Trend"] = df["Close"].rolling(self.config.trend_sma_period).mean()

        # RSI(5)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 3 日累計跌幅
        n = self.config.decline_lookback
        df["Decline_3d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件 1：上升趨勢（收盤 > SMA(50)）
        cond_trend = df["Close"] > df["SMA_Trend"]

        # 條件 2：短期超賣（RSI(5) < 30）
        cond_oversold = df["RSI"] < self.config.rsi_threshold

        # 條件 3：回調幅度（3 日跌幅 >= 2%）
        cond_decline = df["Decline_3d"] <= self.config.decline_threshold

        df["Signal"] = cond_trend & cond_oversold & cond_decline

        # Cooldown
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
        logger.info("DIA-010: Detected %d RSI(5) trend pullback signals", signal_count)
        return df

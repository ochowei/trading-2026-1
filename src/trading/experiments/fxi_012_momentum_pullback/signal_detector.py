"""
FXI-012 Signal Detector: Momentum Breakout Pullback Continuation

進場條件（五項同時成立 — Att1 Baseline）：
1. 近 5 日內曾創 20 日 Donchian 新高（breakout freshness）
2. Close > SMA(50)（確認中期趨勢向上）
3. 當前 Close 相對於 5 日高點回檔 -2% 至 -5%（淺層回檔）
4. RSI(14) ∈ [40, 60]（中性 — 非超買非深度超賣）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_012_momentum_pullback.config import FXI012Config

logger = logging.getLogger(__name__)


class FXI012SignalDetector(BaseSignalDetector):
    """FXI-012：Donchian 新高 + 淺回檔 + SMA 趨勢 + RSI 中性 訊號偵測器"""

    def __init__(self, config: FXI012Config):
        self.config = config

    @staticmethod
    def _compute_rsi(close: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.where(avg_loss > 0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian 上軌（shift(1) 避免 look-ahead）：前 N 日的最高價
        donchian = df["High"].shift(1).rolling(self.config.donchian_period).max()
        df["Donchian_Upper"] = donchian

        # 是否今日 High 突破 Donchian 上軌（creating new 20d high）
        df["IsNewHigh"] = df["High"] > donchian

        # Breakout freshness: 近 N 日內曾有 IsNewHigh
        recency = self.config.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # SMA(50) 趨勢過濾
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # 5 日高點回檔（當前 Close 相對於 5 日高點）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(14)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_pullback_low = df["Pullback"] <= self.config.pullback_min
        cond_pullback_high = df["Pullback"] >= self.config.pullback_max
        cond_rsi_min = df["RSI"] >= self.config.rsi_min
        cond_rsi_max = df["RSI"] <= self.config.rsi_max

        df["Signal"] = (
            cond_recent_new_high
            & cond_trend
            & cond_pullback_low
            & cond_pullback_high
            & cond_rsi_min
            & cond_rsi_max
        )

        # 冷卻機制
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap_days = len(df.loc[last_signal:idx]) - 1
                if gap_days <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("FXI-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FXI-012: Detected %d momentum pullback signals", signal_count)
        return df

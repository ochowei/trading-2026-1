"""
IBIT-007 訊號偵測器：Keltner 通道下軌 + 回檔 + 反轉 K 線均值回歸
(IBIT-007 Signal Detector: Keltner Lower Band + Pullback + Reversal Bar MR)

進場條件（同時成立）：
1. Close < EMA(20) − 2.0 × ATR(10)（波動率自適應超賣）
2. 10 日高點回檔 ≤ -8%（深度過濾，淺回調不算）
3. 10 日回檔 ≥ -25%（崩盤上限）
4. Close > Open（日內反轉 K 線）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ibit_007_keltner_lower_mr.config import IBIT007Config

logger = logging.getLogger(__name__)


class IBIT007SignalDetector(BaseSignalDetector):
    """IBIT-007：Keltner 下軌 + 回檔 + 反轉 K 線 訊號偵測器"""

    def __init__(self, config: IBIT007Config):
        self.config = config

    @staticmethod
    def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.ewm(span=period, min_periods=period, adjust=False).mean()

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Keltner Channel lower band
        df["EMA"] = df["Close"].ewm(span=self.config.ema_period, adjust=False).mean()
        df["ATR"] = self._compute_atr(df, self.config.atr_period)
        df["Keltner_Lower"] = df["EMA"] - self.config.keltner_multiplier * df["ATR"]

        # 回檔深度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_keltner = df["Close"] < df["Keltner_Lower"]
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_reversal = df["Close"] > df["Open"]
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = cond_keltner & cond_pullback & cond_upper & cond_reversal & cond_wr

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
            logger.info("IBIT-007: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("IBIT-007: Detected %d Keltner-lower reversion signals", signal_count)
        return df

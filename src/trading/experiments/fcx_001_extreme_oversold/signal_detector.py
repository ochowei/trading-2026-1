"""
FCX 極端超賣均值回歸訊號偵測器
FCX Extreme Oversold Mean Reversion Signal Detector

進場條件（全部滿足）：
1. 收盤價低於 60 日高點 ≥ 20%（深度回撤）
2. RSI(10) < 25（極端超賣）
3. 收盤價低於 SMA50 超過 10%（乖離過大）
4. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_001_extreme_oversold.config import FCXExtremeOversoldConfig

logger = logging.getLogger(__name__)


class FCXExtremeOversoldDetector(BaseSignalDetector):
    """FCX 極端超賣訊號偵測器"""

    def __init__(self, config: FCXExtremeOversoldConfig):
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

        # 1. 回撤指標：從 N 日高點的跌幅
        df["High_N"] = df["High"].rolling(window=self.config.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # 2. RSI
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 3. SMA 與乖離率
        df["SMA"] = df["Close"].rolling(window=self.config.sma_period).mean()
        df["SMA_Deviation"] = (df["Close"] - df["SMA"]) / df["SMA"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 三重條件
        cond_drawdown = df["Drawdown"] <= self.config.drawdown_threshold
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_sma_dev = df["SMA_Deviation"] <= self.config.sma_deviation_threshold

        df["Signal"] = cond_drawdown & cond_rsi & cond_sma_dev

        # 冷卻期：抑制間隔太近的訊號
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
        logger.info(f"FCX: Detected {signal_count} extreme oversold signals")
        return df

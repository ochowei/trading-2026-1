"""
FCX-008 Att3 訊號偵測器：2日急跌 + 極端超賣均值回歸
FCX-008 Att3 Signal Detector: Sharp Drop + Extreme Oversold

進場條件（全部滿足）：
1. 收盤價低於 60 日高點 >= 18%（深度回撤，同 FCX-001）
2. RSI(10) < 28（極端超賣，同 FCX-001）
3. 收盤價低於 SMA(50) 超過 8%（乖離過大，同 FCX-001）
4. 2日價格跌幅 <= -5%（急跌確認，過濾慢磨下跌）
5. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_008_trend_pullback.config import FCX008Config

logger = logging.getLogger(__name__)


class FCX008SignalDetector(BaseSignalDetector):
    """FCX-008 2日急跌 + 極端超賣訊號偵測器"""

    def __init__(self, config: FCX008Config):
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

        # 4. 2日價格跌幅
        df["Two_Day_Drop"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # FCX-001 三重條件
        cond_drawdown = df["Drawdown"] <= self.config.drawdown_threshold
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_sma_dev = df["SMA_Deviation"] <= self.config.sma_deviation_threshold

        # 新增：2日急跌過濾
        cond_drop = df["Two_Day_Drop"] <= self.config.two_day_drop_threshold

        df["Signal"] = cond_drawdown & cond_rsi & cond_sma_dev & cond_drop

        # 冷卻期
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
        logger.info("FCX-008: Detected %d sharp-drop extreme oversold signals", signal_count)
        return df

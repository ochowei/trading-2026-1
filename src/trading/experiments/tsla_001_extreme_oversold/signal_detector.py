"""
TSLA 極端超賣均值回歸訊號偵測器
TSLA Extreme Oversold Mean Reversion Signal Detector

進場條件（全部滿足）：
1. 收盤價低於 60 日高點 20-45%（回撤範圍過濾）
2. RSI(2) < 15（極端短期超賣）
3. 2日跌幅 >= 6%（確認恐慌拋售）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_001_extreme_oversold.config import TSLAExtremeOversoldConfig

logger = logging.getLogger(__name__)


class TSLAExtremeOversoldDetector(BaseSignalDetector):
    """TSLA 極端超賣訊號偵測器"""

    def __init__(self, config: TSLAExtremeOversoldConfig):
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

        # 2. RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 3. 2日跌幅
        df["Two_Day_Drop"] = df["Close"].pct_change(periods=2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回撤範圍過濾（下限 + 上限）
        cond_drawdown_lower = df["Drawdown"] <= self.config.drawdown_threshold
        cond_drawdown_upper = df["Drawdown"] >= self.config.drawdown_upper
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_drop = df["Two_Day_Drop"] <= self.config.two_day_drop

        df["Signal"] = cond_drawdown_lower & cond_drawdown_upper & cond_rsi & cond_drop

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
        logger.info(f"TSLA: Detected {signal_count} extreme oversold signals")
        return df

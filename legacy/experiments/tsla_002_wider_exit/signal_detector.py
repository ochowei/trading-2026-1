"""
TSLA-002 訊號偵測器：寬出場均值回歸
TSLA-002 Signal Detector: Wider Exit Mean Reversion

進場條件與 TSLA-001 完全相同：
1. 收盤價低於 60 日高點 20-45%（回撤範圍過濾）
2. RSI(2) < 15（極端短期超賣）
3. 2日跌幅 >= 6%（確認恐慌拋售）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_002_wider_exit.config import TSLAWiderExitConfig

logger = logging.getLogger(__name__)


class TSLAWiderExitDetector(BaseSignalDetector):
    """TSLA 寬出場訊號偵測器"""

    def __init__(self, config: TSLAWiderExitConfig):
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

        df["High_N"] = df["High"].rolling(window=self.config.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High_N"]) / df["High_N"]
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)
        df["Two_Day_Drop"] = df["Close"].pct_change(periods=2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_drawdown_lower = df["Drawdown"] <= self.config.drawdown_threshold
        cond_drawdown_upper = df["Drawdown"] >= self.config.drawdown_upper
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_drop = df["Two_Day_Drop"] <= self.config.two_day_drop

        df["Signal"] = cond_drawdown_lower & cond_drawdown_upper & cond_rsi & cond_drop

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
        logger.info("TSLA: Detected %d extreme oversold signals", signal_count)
        return df

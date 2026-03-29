"""
TSM-003 訊號偵測器：回檔 + RSI(2) 極端超賣均值回歸
(TSM-003 Signal Detector: Pullback + RSI(2) Extreme Oversold Mean Reversion)

進場條件（全部滿足）：
1. 10 日高點回檔 >= 8%（結構性下跌過濾）
2. RSI(2) < 15（短期動量耗竭）
3. 收盤位置 >= 40%（日內反轉確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_003_rsi2_reversal.config import TSMRsi2Config

logger = logging.getLogger(__name__)


class TSMRsi2SignalDetector(BaseSignalDetector):
    def __init__(self, config: TSMRsi2Config):
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

        # 回檔幅度（10日高點）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback & cond_rsi & cond_reversal

        # Cooldown mechanism
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
        logger.info("TSM-003: Detected %d Pullback+RSI(2) signals", signal_count)
        return df

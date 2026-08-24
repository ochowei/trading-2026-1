"""
IWM-010 訊號偵測器：回檔範圍 + RSI(2) 混合均值回歸
(IWM-010 Signal Detector: Pullback Range + RSI(2) Hybrid Mean Reversion)

進場條件（Att2 最終版）：
1. 10 日最高價回檔 3-10%（結構性過濾）
2. RSI(2) < 10（極端超賣）
3. 2 日累計跌幅 >= 2.5%（幅度過濾）
4. 收盤位置 >= 40%（日內反轉確認）
5. 冷卻期 5 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.iwm_010_pullback_rsi2_hybrid.config import IWM010Config

logger = logging.getLogger(__name__)


class IWM010SignalDetector(BaseSignalDetector):
    def __init__(self, config: IWM010Config):
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

        # 10 日最高價回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["High_N"] - df["Close"]) / df["High_N"]

        # RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2 日累計跌幅
        d = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(d)) / df["Close"].shift(d)

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔範圍過濾
        cond_pullback = (df["Pullback"] >= self.config.pullback_min) & (
            df["Pullback"] <= self.config.pullback_max
        )

        # RSI(2) 極端超賣
        cond_rsi = df["RSI"] < self.config.rsi_threshold

        # 2 日跌幅
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold

        # 反轉K線確認
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback & cond_rsi & cond_decline & cond_reversal

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
        logger.info("IWM-010: Detected %d pullback range + RSI(2) hybrid signals", signal_count)
        return df

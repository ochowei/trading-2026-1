"""
GLD-010 訊號偵測器：動量回檔
(GLD-010 Signal Detector: Momentum Pullback)

進場條件（全部滿足）：
1. ROC(20) > 3%（過去20日有強勢上漲動能）
2. 收盤價低於 5 日高點 ≥ 1.5%（短期回檔）
3. Close > SMA(50)（確認仍在上升趨勢中）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_010_momentum_pullback.config import GLD010Config

logger = logging.getLogger(__name__)


class GLD010SignalDetector(BaseSignalDetector):
    def __init__(self, config: GLD010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # ROC (Rate of Change)
        n = self.config.roc_period
        df["ROC"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 短期回檔幅度（5日回看）
        pb_n = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(pb_n).max()
        df["Pullback_5d"] = (df["Close"] - df["High_5d"]) / df["High_5d"]

        # SMA(50)
        df["SMA50"] = df["Close"].rolling(self.config.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_momentum = df["ROC"] > self.config.roc_threshold
        cond_pullback = df["Pullback_5d"] <= self.config.pullback_threshold
        cond_trend = df["Close"] > df["SMA50"]

        df["Signal"] = cond_momentum & cond_pullback & cond_trend

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
        logger.info("GLD-010: Detected %d Momentum Pullback signals", signal_count)
        return df

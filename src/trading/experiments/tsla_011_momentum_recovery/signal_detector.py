"""
TSLA-011 訊號偵測器：回檔後突破
TSLA-011 Signal Detector: Breakout from Oversold Base

進場條件（全部滿足）：
1. 近 20 日內最深回撤 <= -20%（近期有顯著回檔）
2. 收盤 > 過去 20 日最高價（突破近期高點，確認回復動能）
3. 冷卻期 20 交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_011_momentum_recovery.config import TSLABreakoutConfig

logger = logging.getLogger(__name__)


class TSLABreakoutDetector(BaseSignalDetector):
    """TSLA 回檔後突破訊號偵測器"""

    def __init__(self, config: TSLABreakoutConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["High_60"] = df["High"].rolling(window=self.config.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High_60"]) / df["High_60"]

        df["Min_DD_Recent"] = df["Drawdown"].rolling(window=self.config.pullback_lookback).min()

        df["High_Prev_N"] = df["High"].shift(1).rolling(window=self.config.breakout_lookback).max()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Min_DD_Recent"] <= self.config.pullback_threshold
        cond_breakout = df["Close"] > df["High_Prev_N"]

        df["Signal"] = cond_pullback & cond_breakout

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
        logger.info("TSLA: Detected %d breakout signals", signal_count)
        return df

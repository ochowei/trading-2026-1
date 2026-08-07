"""
NVDA-006 訊號偵測器：Relative Strength Momentum Pullback
NVDA-006 Signal Detector: Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. NVDA 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-8%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.nvda_006_relative_strength.config import (
    NVDARelativeStrengthConfig,
)

logger = logging.getLogger(__name__)


class NVDARelativeStrengthDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """NVDA Relative Strength Momentum Pullback 訊號偵測器"""

    def __init__(self, config: NVDARelativeStrengthConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies SMH already aligned as-of to every
        # primary decision session.
        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # NVDA 和 SMH 的 20日報酬
        period = self.config.relative_strength_period
        df["NVDA_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)

        # 相對強度 = NVDA 報酬 - SMH 報酬
        df["Relative_Strength"] = df["NVDA_Return"] - df["SMH_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # NVDA 相對 SMH 有超額表現
        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min

        # 短期回調在範圍內
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )

        # 上升趨勢
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_rs & cond_pullback & cond_trend

        # 冷卻機制
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
        logger.info("NVDA: Detected %d relative strength signals", signal_count)
        return df

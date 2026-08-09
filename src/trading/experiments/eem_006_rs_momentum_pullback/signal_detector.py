"""
EEM-006 訊號偵測器：RS Momentum Pullback
EEM-006 Signal Detector: Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. EEM 20日報酬 - SPY 20日報酬 >= 3%（EM 相對 DM 超額表現）
2. 5日高點回撤 2-4%（短暫整理，非崩盤）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.eem_006_rs_momentum_pullback.config import (
    EEMRSMomentumConfig,
)

logger = logging.getLogger(__name__)


class EEMRSMomentumDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """EEM RS Momentum Pullback 訊號偵測器"""

    def __init__(self, config: EEMRSMomentumConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies SPY aligned as-of to every primary decision session.
        spy_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # EEM 和 SPY 的 20日報酬
        period = self.config.relative_strength_period
        df["EEM_Return"] = df["Close"].pct_change(period)
        df["SPY_Return"] = spy_df["Close"].pct_change(period)

        # 相對強度 = EEM 報酬 - SPY 報酬
        df["Relative_Strength"] = df["EEM_Return"] - df["SPY_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # EEM 相對 SPY 有超額表現
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
        logger.info("EEM: Detected %d relative strength momentum signals", signal_count)
        return df

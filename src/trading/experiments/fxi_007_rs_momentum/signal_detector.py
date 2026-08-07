"""
FXI-007 訊號偵測器：Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. FXI 20日報酬 - EEM 20日報酬 >= 3%（中國相對 EM 超額表現）
2. 5日高點回撤 2-5%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.fxi_007_rs_momentum.config import FXI007Config

logger = logging.getLogger(__name__)


class FXI007SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """FXI Relative Strength Momentum Pullback 訊號偵測器"""

    def __init__(self, config: FXI007Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        ref_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["FXI_Return"] = df["Close"].pct_change(period)
        df["EEM_Return"] = ref_df["Close"].pct_change(period)

        df["Relative_Strength"] = df["FXI_Return"] - df["EEM_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_rs & cond_pullback & cond_trend

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
        logger.info("FXI-007: Detected %d relative strength signals", signal_count)
        return df

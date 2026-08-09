"""
EWJ-004 訊號偵測器：Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. EWJ 20日報酬 - 參考標的 20日報酬 >= RS 門檻（日本相對超額表現）
2. 5日高點回撤 1.5-4%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.ewj_004_rs_momentum.config import EWJ004Config

logger = logging.getLogger(__name__)


class EWJ004SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """EWJ Relative Strength Momentum Pullback 訊號偵測器"""

    def __init__(self, config: EWJ004Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        ref_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["EWJ_Return"] = df["Close"].pct_change(period)
        df["Ref_Return"] = ref_df["Close"].pct_change(period)

        df["Relative_Strength"] = df["EWJ_Return"] - df["Ref_Return"]

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
        logger.info("EWJ-004: Detected %d relative strength signals", signal_count)
        return df

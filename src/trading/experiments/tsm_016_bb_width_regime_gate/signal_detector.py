"""
TSM-016 訊號偵測器：BB-Width Regime Gate on RS Momentum Pullback

進場條件（全部滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 訊號日 5 日報酬 <= ret_5d_max（rally exhaustion 過濾）
5. BB(20, 2) Width / Close <= bb_width_max（calm regime gate, lesson #23）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_016_bb_width_regime_gate.config import (
    TSMBBWidthRegimeGateConfig,
)

logger = logging.getLogger(__name__)


class TSMBBWidthRegimeGateDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM BB-Width Regime Gate 訊號偵測器"""

    def __init__(self, config: TSMBBWidthRegimeGateConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_5d"] = df["Close"].pct_change(5)

        # BB-Width Regime Gate (lesson #23 cross-strategy port)
        bb_mid = df["Close"].rolling(self.config.bb_period).mean()
        bb_std = df["Close"].rolling(self.config.bb_period).std()
        bb_upper = bb_mid + self.config.bb_std * bb_std
        bb_lower = bb_mid - self.config.bb_std * bb_std
        df["BB_Width_Ratio"] = (bb_upper - bb_lower) / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max
        cond_bb = df["BB_Width_Ratio"] <= self.config.bb_width_max

        df["Signal"] = cond_rs & cond_pullback & cond_trend & cond_5d & cond_bb

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
        logger.info("TSM: Detected %d filtered signals", signal_count)
        return df

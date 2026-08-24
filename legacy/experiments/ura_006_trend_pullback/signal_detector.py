"""
URA-006 訊號偵測器：相對強度回調買入
(URA-006 Signal Detector: Relative Strength Pullback Entry)

進場條件（全部滿足）：
1. URA 20日報酬 - XLE 20日報酬 >= 8%（板塊超額表現）
2. Close > SMA(50)（價格位於趨勢上方）
3. 5日高點回撤 3-8%（短期回調提供進場機會）
4. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.ura_006_trend_pullback.config import URATrendPullbackConfig

logger = logging.getLogger(__name__)


class URATrendPullbackDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """URA 相對強度回調訊號偵測器"""

    def __init__(self, config: URATrendPullbackConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies the reference series already aligned
        # as-of to every primary decision session.
        ref_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        # SMA 趨勢
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # URA 和 XLE 的 20日報酬
        period = self.config.relative_strength_period
        df["URA_Return"] = df["Close"].pct_change(period)
        df["XLE_Return"] = ref_df["Close"].pct_change(period)

        # 相對強度 = URA 報酬 - XLE 報酬
        df["Relative_Strength"] = df["URA_Return"] - df["XLE_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：URA 相對 XLE 有超額表現
        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min

        # 條件二：價格在趨勢上方
        cond_above_trend = df["Close"] > df["SMA_Trend"]

        # 條件三：短期回調在範圍內
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )

        df["Signal"] = cond_rs & cond_above_trend & cond_pullback

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
            logger.info("URA-006: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA-006: Detected %d RS pullback signals", signal_count)
        return df

"""
INDA-007 訊號偵測器：Relative Strength Momentum Pullback
INDA-007 Signal Detector: Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. INDA 20日報酬 - EEM 20日報酬 >= 2.5%（印度相對 EM 超額表現）
2. 5日高點回撤 1.5-4%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. ATR(5)/ATR(20) > 1.10（波動率放大，急跌恐慌環境）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.inda_007_rs_momentum.config import INDA007Config

logger = logging.getLogger(__name__)


class INDA007SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """INDA Relative Strength Momentum Pullback 訊號偵測器"""

    def __init__(self, config: INDA007Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # EEM 由 shared followup data bundle 提供，缺漏時 fail closed。
        ref_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # INDA 和 EEM 的 20日報酬
        period = self.config.relative_strength_period
        df["INDA_Return"] = df["Close"].pct_change(period)
        df["EEM_Return"] = ref_df["Close"].pct_change(period)

        # 相對強度 = INDA 報酬 - EEM 報酬
        df["Relative_Strength"] = df["INDA_Return"] - df["EEM_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        # ATR 波動率比率
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Short"] = tr.rolling(self.config.atr_short_period).mean()
        df["ATR_Long"] = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = df["ATR_Short"] / df["ATR_Long"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # INDA 相對 EEM 有超額表現
        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min

        # 短期回調在範圍內
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )

        # 上升趨勢
        cond_trend = df["Close"] > df["SMA_Trend"]

        # ATR 波動率放大（急跌恐慌環境）
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_rs & cond_pullback & cond_trend & cond_atr

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
        logger.info("INDA-007: Detected %d relative strength signals", signal_count)
        return df

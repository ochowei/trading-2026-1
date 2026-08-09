"""
TSM-018 訊號偵測器：ATR(5)/ATR(20) BAND on RS Momentum Pullback

進場條件（全部滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%
3. 收盤價 > SMA(50)
4. 5 日報酬 <= +10.5%（rally exhaustion 過濾，沿用 TSM-011 Att3）
5. ATR(5)/ATR(20) BAND ∈ (atr_ratio_floor, atr_ratio_ceiling]
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_018_atr_band_rs.config import TSMAtrBandRSConfig

logger = logging.getLogger(__name__)


class TSMAtrBandRSDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM ATR(5)/ATR(20) BAND on RS Momentum 訊號偵測器"""

    def __init__(self, config: TSMAtrBandRSConfig):
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

        # ATR ratio（vol-acceleration BAND 維度）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast_period).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow_period).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max
        cond_atr_floor = df["ATR_ratio"] > self.config.atr_ratio_floor
        cond_atr_ceiling = df["ATR_ratio"] <= self.config.atr_ratio_ceiling

        df["Signal"] = (
            cond_rs & cond_pullback & cond_trend & cond_5d & cond_atr_floor & cond_atr_ceiling
        )

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
        logger.info("TSM-018: Detected %d filtered signals", signal_count)
        return df

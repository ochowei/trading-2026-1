"""
NVDA-015 訊號偵測器：Multi-Week Regime-Aware Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. NVDA 20日報酬 - SMH 20日報酬 >= relative_strength_min
2. 5日高點回撤在 [pullback_min, pullback_max]
3. Close > SMA(sma_trend_period)
4. SMA(sma_regime_short) >= sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered multi-week SMA regime gate）
5. （可選）ATR(atr_regime_short) <= vol_regime_max_ratio × ATR(atr_regime_long)
6. 冷卻 cooldown_days 個交易日

設計依據：lesson #22 + ATR vol regime（NVDA-013 Att3 雙重 gate）
首次跨策略類型移植至 RS Momentum Pullback 框架。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.nvda_015_regime_rs.config import NVDA015Config

logger = logging.getLogger(__name__)


class NVDA015RegimeRSDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """NVDA-015 訊號偵測器"""

    def __init__(self, config: NVDA015Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies SMH already aligned as-of to every
        # primary decision session.
        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        # === SMA trend filter (NVDA-006) ===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === Relative Strength = NVDA pct_change - SMH pct_change ===
        period = self.config.relative_strength_period
        df["NVDA_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["NVDA_Return"] - df["SMH_Return"]

        # === 5d pullback ===
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        # === Multi-week SMA regime (lesson #22) ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === ATR regime (NVDA-013 vol gate) ===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        signal = cond_rs & cond_pullback & cond_trend & cond_regime_trend & cond_regime_vol
        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
            logger.info(
                "NVDA-015: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-015: Detected %d regime-aware RS momentum signals",
            signal_count,
        )
        return df

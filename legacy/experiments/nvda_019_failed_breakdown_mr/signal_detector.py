"""
NVDA-019 訊號偵測器：Failed Breakdown Reversal Mean Reversion

進場條件（全部滿足）：
1. 過去 breakdown_lookback_days 日內，曾發生 Low <= Donchian_Lower(donchian_period)
2. 今日 Close > Donchian_Lower（站回支撐）
3. 今日 Close > Open（陽線確認）
4. SMA(sma_regime_short) >= sma_regime_ratio_min × SMA(sma_regime_long)（lesson #22）
5. （可選）ATR(atr_regime_short) <= vol_regime_max_ratio × ATR(atr_regime_long)
6. 冷卻 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_019_failed_breakdown_mr.config import NVDA019Config

logger = logging.getLogger(__name__)


class NVDA019FailedBreakdownDetector(BaseSignalDetector):
    """NVDA-019 訊號偵測器：Failed Breakdown Reversal MR"""

    def __init__(self, config: NVDA019Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Donchian Lower (rolling N-day low, excluding today) ===
        df["Donchian_Lower"] = df["Low"].shift(1).rolling(self.config.donchian_period).min()

        # === Breakdown day: today's Low touched/broke prior Donchian Lower ===
        df["IsBreakdown"] = df["Low"] <= df["Donchian_Lower"]

        # === Recent breakdown within last K days (含今日) ===
        df["RecentBreakdown"] = (
            df["IsBreakdown"].rolling(self.config.breakdown_lookback_days, min_periods=1).max()
            >= 1.0
        )

        # === Breakdown depth：過去 K 日內最低 Low 與今日 Close 的相對深度 ===
        breakdown_low = df["Low"].rolling(self.config.breakdown_lookback_days, min_periods=1).min()
        df["BreakdownDepth"] = (df["Close"] - breakdown_low) / df["Close"]

        # === SMA trend regime (lesson #22) ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === ATR(N) via True Range Wilder smoothing equivalent (rolling mean for simplicity) ===
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

        cond_recent_breakdown = df["RecentBreakdown"]
        cond_above_support = df["Close"] > df["Donchian_Lower"]
        cond_depth = df["BreakdownDepth"] >= self.config.min_breakdown_depth
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        signal = (
            cond_recent_breakdown
            & cond_above_support
            & cond_depth
            & cond_regime_trend
            & cond_regime_vol
        )

        if self.config.require_bullish_close:
            signal = signal & (df["Close"] > df["Open"])

        if self.config.require_close_above_prev_high:
            signal = signal & (df["Close"] > df["High"].shift(1))

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
                "NVDA-019: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-019: Detected %d failed-breakdown reversal signals",
            signal_count,
        )
        return df

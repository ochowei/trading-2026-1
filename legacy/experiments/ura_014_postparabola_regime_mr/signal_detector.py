"""
URA-014 signal detector: Post-Parabolic Long-Horizon Regime-Gated Capitulation MR

Entry conditions (all must be met) — URA-013 Att2 base + one new gate:
1. 10-day high pullback >= 10% (depth, same as URA-004)
2. 10-day high pullback <= 20% (crash isolation, same as URA-004)
3. RSI(2) < 15 (short-period oversold, same as URA-004)
4. 2-day decline <= -3% (panic confirmation, same as URA-004)
5. ATR(5)/ATR(20) BAND [1.00, 1.50] (URA-012 Att2 mirror-image filter)
6. 5-day cumulative return >= -9.0% (URA-013 Att2 multi-period cap)
7. Prior 60-day cumulative return <= +35% (NEW: post-parabolic regime gate;
   reject dips that are the early unwind of a fresh parabolic blow-off,
   lesson #19 family extension to a long-horizon CEILING)
8. Cooldown 10 trading days
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_014_postparabola_regime_mr.config import URA014Config

logger = logging.getLogger(__name__)


class URA014SignalDetector(BaseSignalDetector):
    """URA-014 post-parabolic long-horizon regime-gated capitulation MR detector"""

    def __init__(self, config: URA014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        df["TwoDayDecline"] = df["Close"].pct_change(2)

        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        df["MultiPeriodReturn"] = df["Close"].pct_change(self.config.multi_period_lookback)

        # Post-parabolic long-horizon regime gate input
        df["RunupReturn"] = df["Close"].pct_change(self.config.runup_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_decline = df["TwoDayDecline"] <= self.config.two_day_decline
        cond_vol_floor = df["ATR_Ratio"] >= self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling
        cond_multi_cap = df["MultiPeriodReturn"] >= self.config.multi_period_cap
        cond_runup_ceiling = df["RunupReturn"] <= self.config.runup_ceiling

        df["Signal"] = (
            cond_pullback
            & cond_upper
            & cond_rsi
            & cond_decline
            & cond_vol_floor
            & cond_vol_ceiling
            & cond_multi_cap
            & cond_runup_ceiling
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
            logger.info(
                "URA-014: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("URA-014: Detected %d post-parabolic regime-gated MR signals", signal_count)
        return df

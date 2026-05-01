"""
URA-012 signal detector: Volatility-Acceleration-Bounded MR (ATR BAND)

Entry conditions (all must be met):
1. 10-day high pullback >= 10% (depth, same as URA-004)
2. 10-day high pullback <= 20% (crash isolation, same as URA-004)
3. RSI(2) < 15 (short-period oversold, same as URA-004)
4. 2-day decline <= -3% (panic confirmation, same as URA-004)
5. ATR(5)/ATR(20) >= 1.00 (FLOOR — exclude calm-grind low-vol regime
                           that produces Part B losers; mirror image of
                           Part A SL distribution)
6. ATR(5)/ATR(20) <= 1.50 (CEILING — exclude in-crash acceleration phase
                           that produces Part A losers; cross-asset port
                           from FXI-014/CIBR-014)
7. Cooldown 10 trading days
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_012_atr_band_mr.config import URA012Config

logger = logging.getLogger(__name__)


class URA012SignalDetector(BaseSignalDetector):
    """URA-012 ATR ratio BAND mean reversion signal detector"""

    def __init__(self, config: URA012Config):
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

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_decline = df["TwoDayDecline"] <= self.config.two_day_decline
        cond_vol_floor = df["ATR_Ratio"] >= self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling

        df["Signal"] = (
            cond_pullback & cond_upper & cond_rsi & cond_decline & cond_vol_floor & cond_vol_ceiling
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
                "URA-012: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("URA-012: Detected %d ATR-band MR signals", signal_count)
        return df

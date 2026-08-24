"""
SIVR-018 signal detector: Capitulation-Strength Filter Mean Reversion

Entry conditions:
  1. Pullback >= 7% from 10-day high (SIVR-005 base)
  2. Pullback <= 15% from 10-day high (crash isolation, SIVR-005 base)
  3. Williams %R(10) <= -80 (oversold, SIVR-005 base)
  4. (Optional) RSI(14) bullish hook: today >= 5d low + delta AND 5d
     low <= max_min (SIVR-015 Att1)
  5. (Optional) ATR(5)/ATR(20) within [floor, ceiling] BAND
  6. (Optional) 1-day return >= one_day_cap (lesson #19 1d cap, filters
     regime-shift single-day SLs)
  7. (Optional) 3-day return >= three_day_cap (lesson #19 3d cap, filters
     regime-shift multi-day SLs)
  8. Cooldown 10 trading days
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_018_atr_band_mr.config import SIVR018Config

logger = logging.getLogger(__name__)


class SIVR018SignalDetector(BaseSignalDetector):
    """SIVR-018 capitulation-strength filter mean reversion signal detector"""

    def __init__(self, config: SIVR018Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        if self.config.use_rsi_hook:
            rsi_n = self.config.rsi_period
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta).where(delta < 0, 0.0)
            avg_gain = gain.rolling(rsi_n).mean()
            avg_loss = loss.rolling(rsi_n).mean()
            rs = avg_gain / avg_loss.replace(0, float("nan"))
            df["RSI"] = 100 - (100 / (1 + rs))

            hook_n = self.config.rsi_hook_lookback
            df["RSI_Min_N"] = df["RSI"].rolling(hook_n).min()
            df["RSI_Hook_Delta"] = df["RSI"] - df["RSI_Min_N"]

        if self.config.use_atr_band:
            tr = pd.concat(
                [
                    df["High"] - df["Low"],
                    (df["High"] - df["Close"].shift(1)).abs(),
                    (df["Low"] - df["Close"].shift(1)).abs(),
                ],
                axis=1,
            ).max(axis=1)
            df["ATR_Ratio"] = (
                tr.rolling(self.config.atr_short_period).mean()
                / tr.rolling(self.config.atr_long_period).mean()
            )

        if self.config.use_1d_cap:
            df["Ret_1d"] = df["Close"].pct_change(1)

        if self.config.use_3d_cap or self.config.use_3d_floor:
            df["Ret_3d"] = df["Close"].pct_change(3)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        signal = (
            (df["Pullback"] <= self.config.pullback_threshold)
            & (df["Pullback"] >= self.config.pullback_cap)
            & (df["WR"] <= self.config.wr_threshold)
        )

        if self.config.use_rsi_hook:
            signal = (
                signal
                & (df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta)
                & (df["RSI_Min_N"] <= self.config.rsi_hook_max_min)
            )

        if self.config.use_atr_band:
            signal = (
                signal
                & (df["ATR_Ratio"] >= self.config.atr_ratio_floor)
                & (df["ATR_Ratio"] <= self.config.atr_ratio_ceiling)
            )

        if self.config.use_1d_cap:
            signal = signal & (df["Ret_1d"] >= self.config.one_day_cap)

        if self.config.use_3d_cap:
            signal = signal & (df["Ret_3d"] >= self.config.three_day_cap)

        if self.config.use_3d_floor:
            signal = signal & (df["Ret_3d"] <= self.config.three_day_floor)

        df["Signal"] = signal

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
                "SIVR-018: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SIVR-018: Detected %d capitulation-strength MR signals", signal_count)
        return df

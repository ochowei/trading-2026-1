"""
FXI-014 signal detector: Volatility-Acceleration-Bounded MR

Entry conditions (all must be met):
1. 10-day high pullback >= 5% (depth filter)
2. 10-day high pullback <= 12% (crash isolation)
3. Williams %R(10) <= -80 (medium-period oversold)
4. Close Position >= 40% (intraday reversal confirmation)
5. ATR(5)/ATR(20) > 1.05 (FLOOR — panic confirmation, lesson #15)
6. ATR(5)/ATR(20) <= 1.40 (CEILING — exclude in-crash acceleration phase,
                           CIBR-014 cross-asset hypothesis)
7. Cooldown 10 trading days
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_014_atr_band_mr.config import FXI014Config

logger = logging.getLogger(__name__)


class FXI014SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI014Config):
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
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol_floor = df["ATR_Ratio"] > self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling

        df["Signal"] = (
            cond_pullback & cond_cap & cond_wr & cond_reversal & cond_vol_floor & cond_vol_ceiling
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
                "FXI-014: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-014: Detected %d ATR-band MR signals", signal_count)
        return df

"""
FXI-008 signal detector: Stochastic %K/%D crossover mean reversion

Entry conditions (all must be met):
1. 10-day high pullback in [-12%, -5%] (depth + crash isolation)
2. Williams %R(10) <= -80 (short-term raw oversold)
3. Stochastic slow %K(14,3) <= 20 (medium-term smoothed oversold)
4. Close Position >= 40% (intraday reversal confirmation)
5. ATR(5)/ATR(20) > 1.05 (volatility spike)
6. Cooldown 10 trading days

Att3: dual-oscillator confirmation — both WR and Stoch %K must agree on
oversold. Hypothesis: short-term + medium-term-smoothed intersection filters
out one-day noise that fires only one oscillator, improving signal quality.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_008_stochastic_mr.config import FXI008Config

logger = logging.getLogger(__name__)


class FXI008SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI008Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10-day high pullback
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R(10) — short-term raw oversold
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # Stochastic Oscillator: raw %K = (Close - LowN) / (HighN - LowN) * 100
        k_n = self.config.stoch_k_period
        stoch_high = df["High"].rolling(k_n).max()
        stoch_low = df["Low"].rolling(k_n).min()
        raw_k = (df["Close"] - stoch_low) / (stoch_high - stoch_low) * 100
        raw_k = raw_k.where(stoch_high != stoch_low, 50.0)

        # Slow %K: SMA of raw %K over stoch_k_smooth periods
        df["Stoch_K"] = raw_k.rolling(self.config.stoch_k_smooth).mean()

        # %D: SMA of slow %K over stoch_d_period periods
        df["Stoch_D"] = df["Stoch_K"].rolling(self.config.stoch_d_period).mean()

        # Close Position within day's range
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR ratio (short-term vol spike vs long-term)
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
        cond_stoch_oversold = df["Stoch_K"] <= self.config.stoch_k_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = (
            cond_pullback & cond_cap & cond_wr & cond_stoch_oversold & cond_reversal & cond_vol
        )

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
                "FXI-008: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-008: Detected %d Stochastic crossover MR signals", signal_count)
        return df

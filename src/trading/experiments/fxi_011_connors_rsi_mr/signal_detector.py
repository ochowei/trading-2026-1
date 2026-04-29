"""
FXI-011 signal detector: Connor's RSI Mean Reversion (Att3)

Entry conditions (all must be met):
1. 10-day high pullback >= 5% (FXI-005 depth filter)
2. 10-day high pullback <= 12% (crash isolation, FXI lesson)
3. Williams %R(10) <= -80 (FXI-005 primary oversold gate)
4. Connor's RSI(3,2,100) <= 25 (additional persistence/history filter)
5. Close Position >= 40% (intraday reversal confirmation)
6. ATR(5)/ATR(20) > 1.05 (FXI-005 volatility spike filter)
7. Cooldown 10 trading days

CRSI = (RSI(3) + Streak_RSI(2) + PercentRank(1d_return, 100d)) / 3
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_011_connors_rsi_mr.config import FXI011Config

logger = logging.getLogger(__name__)


def _wilder_rsi(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothed RSI on an arbitrary series."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi = rsi.fillna(100.0).where(avg_loss > 0, 100.0)
    rsi = rsi.where(avg_gain > 0, 0.0).where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    return rsi


def _streak_series(close: pd.Series) -> pd.Series:
    """Consecutive up/down day count: +N for N up days, -N for N down days, 0 on flat."""
    direction = np.sign(close.diff().fillna(0.0).to_numpy())
    streak = np.zeros(len(direction), dtype=float)
    cur = 0
    for i, d in enumerate(direction):
        if d > 0:
            cur = cur + 1 if cur > 0 else 1
        elif d < 0:
            cur = cur - 1 if cur < 0 else -1
        else:
            cur = 0
        streak[i] = cur
    return pd.Series(streak, index=close.index)


def _percent_rank(series: pd.Series, period: int) -> pd.Series:
    """Rolling %Rank: percentage of values in the window strictly less than current."""

    def _rank(window: np.ndarray) -> float:
        ref = window[-1]
        prior = window[:-1]
        return float((prior < ref).sum()) / float(len(prior)) * 100.0

    return series.rolling(period + 1).apply(_rank, raw=True)


def compute_crsi(
    close: pd.Series,
    rsi_period: int = 3,
    streak_period: int = 2,
    rank_period: int = 100,
) -> pd.Series:
    """Connor's RSI = mean of RSI(3), Streak_RSI(2), PercentRank(1d return, 100)."""
    rsi = _wilder_rsi(close, rsi_period)
    streak = _streak_series(close)
    streak_rsi = _wilder_rsi(streak, streak_period)
    rank = _percent_rank(close.pct_change(), rank_period)
    return (rsi + streak_rsi + rank) / 3.0


class FXI011SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI011Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10-day high pullback
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # Connor's RSI
        df["CRSI"] = compute_crsi(
            df["Close"],
            rsi_period=self.config.crsi_rsi_period,
            streak_period=self.config.crsi_streak_period,
            rank_period=self.config.crsi_rank_period,
        )

        # Close position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR ratio
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
        cond_crsi = df["CRSI"] <= self.config.crsi_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_pullback & cond_cap & cond_wr & cond_crsi & cond_reversal & cond_vol

        # Cooldown
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
                "FXI-011: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-011: Detected %d Connor's RSI MR signals", signal_count)
        return df

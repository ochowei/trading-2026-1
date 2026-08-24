"""
FXI-009 signal detector: Failed Breakdown Reversal (Turtle Soup variant).

Entry conditions on day T (all must hold):
1. Prior-day breakdown: Low_{T-1} < rolling N-day min Low over [T-N-1, T-2]
   (day T-1 printed a new N-day low).
2. Reclaim: Close_T > same N-day min Low reference
3. Bullish bar: Close_T > Open_T (intraday accumulation)
4. Williams %R(10) <= -80 at T (still in oversold zone)
5. 20-day high pullback at T >= -12% (crash isolation)
6. ClosePos >= threshold (intraday close strength on reclaim day)
7. Cooldown N_cd trading days.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_009_failed_breakdown_reversal.config import FXI009Config

logger = logging.getLogger(__name__)


class FXI009SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI009Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Prior N-day low reference. For day T, this is min Low over [T-11, T-2].
        # Built as: rolling(N).min() on Low then shift(1) to exclude T-1's own Low,
        # then shift(1) again so column at row T equals min over [T-11, T-2].
        n = self.config.breakdown_lookback
        rolling_min_low = df["Low"].rolling(n).min()
        df["RefLow_prev"] = rolling_min_low.shift(2)  # min over [T-11, T-2]
        df["RefLow_at_Tm1"] = rolling_min_low.shift(1)  # min over [T-10, T-1]

        # Breakdown on day T-1: Low_{T-1} at least `breakdown_depth_pct` below
        # min over [T-11, T-2] (meaningful flush, not cosmetic tick below prior low)
        depth_mult = 1.0 - self.config.breakdown_depth_pct
        df["Breakdown_prev"] = df["Low"].shift(1) <= df["RefLow_prev"] * depth_mult

        # Reclaim on day T: Close_T > min over [T-11, T-2]
        df["Reclaim"] = df["Close"] > df["RefLow_prev"]

        # Bullish bar on day T
        df["Bullish"] = df["Close"] > df["Open"]

        # Williams %R(10)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 20-day high pullback (cap only; depth floor is configurable)
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Close Position within day's range (reclaim-day strength)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_breakdown = df["Breakdown_prev"]
        cond_reclaim = df["Reclaim"]
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_closepos = df["ClosePos"] >= self.config.close_position_threshold

        signal = cond_breakdown & cond_reclaim & cond_wr & cond_cap & cond_closepos
        # Optional depth floor (only applied when pullback_threshold < 0)
        if self.config.pullback_threshold < 0:
            signal = signal & (df["Pullback"] <= self.config.pullback_threshold)
        if self.config.bullish_close_required:
            signal = signal & df["Bullish"]

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
                "FXI-009: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "FXI-009: Detected %d failed-breakdown reversal signals",
            signal_count,
        )
        return df

"""
SIVR-019 signal detector: GVZ Implied-Vol Direction-Floor Filter MR

Entry conditions (all must hold; signal day = T, execution at T+1 open):
  1. Pullback >= 7% from 10-day high (SIVR-005 base)
  2. Pullback <= 15% from 10-day high (crash isolation)
  3. Williams %R(10) <= -80 (oversold)
  4. RSI(14) bullish hook: today >= 5d_low + delta AND 5d_low <= 35
     (SIVR-015 Att1)
  5. ATR(5)/ATR(20) <= 1.20 (SIVR-018 Att3 ATR ceiling)
  6. 3-day return <= -1.0% (SIVR-018 Att3 3d floor)
  7. ^GVZ N-day change >= floor (SIVR-019 NEW: filter sharp gold-vol
     collapse regimes which drag silver MR mid-trade)
  8. Cooldown 10 trading days
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_019_gvz_direction_mr.config import SIVR019Config

logger = logging.getLogger(__name__)


class SIVR019SignalDetector(BaseSignalDetector):
    """SIVR-019 GVZ direction-floor filter MR signal detector"""

    def __init__(self, config: SIVR019Config):
        self.config = config

    def _fetch_gvz_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.gvz_ticker,
                start=start_date,
                progress=False,
                auto_adjust=True,
            )
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception:
            logger.exception("Failed to fetch %s data", self.config.gvz_ticker)
            return None

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

        if self.config.use_3d_floor:
            df["Ret_3d"] = df["Close"].pct_change(3)

        if self.config.use_gvz_direction_filter:
            start_date = df.index[0].strftime("%Y-%m-%d")
            gvz_df = self._fetch_gvz_data(start_date)
            if gvz_df is None or gvz_df.empty:
                logger.error(
                    "Cannot fetch %s; GVZ filter disabled this run",
                    self.config.gvz_ticker,
                )
                df["GVZ_Change_Nd"] = 0.0
            else:
                gvz_close = gvz_df["Close"].reindex(df.index, method="ffill")
                df["GVZ_Change_Nd"] = gvz_close.diff(self.config.gvz_direction_lookback)

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

        if self.config.use_3d_floor:
            signal = signal & (df["Ret_3d"] <= self.config.three_day_floor)

        if self.config.use_gvz_direction_filter:
            signal = signal & (df["GVZ_Change_Nd"] >= self.config.min_gvz_direction_change)

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
                "SIVR-019: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SIVR-019: Detected %d GVZ-direction-gated MR signals", signal_count)
        return df

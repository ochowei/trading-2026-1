"""
SPY-003 訊號偵測器（含 VIX 恐慌過濾）
(SPY-003 Signal Detector with VIX Fear Filter)

進場條件：10 日高點回檔 ≥2.5% + WR(10) ≤ -80 + 收盤位置 ≥40% + VIX ≥ 20，7 天冷卻。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.spy_003_optimized_wr.config import SPYVixFilterConfig

logger = logging.getLogger(__name__)


class SPYVixFilterSignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """SPY-003 detector using a declared, snapshot-aligned VIX series."""

    def __init__(self, config: SPYVixFilterConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return ("^VIX",)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # VIX is supplied by the verified bundle and already aligned as-of to
        # every primary decision session.
        df["VIX"] = self.require_auxiliary("^VIX", df.index)["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vix = df["VIX"] >= self.config.vix_threshold

        df["Signal"] = cond_pullback & cond_wr & cond_reversal & cond_vix

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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

        signal_count = df["Signal"].sum()
        logger.info("SPY-003: Detected %d Pullback+WR+VIX signals", signal_count)
        return df

"""
USO 對稱 TP/SL + 短持倉訊號偵測器 (USO-005)
訊號邏輯與 USO-001 完全相同：10 日高點回檔 ≥ 6% + Williams %R(10) ≤ -80。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_005_symmetric_tight.config import USOSymmetricTightConfig

logger = logging.getLogger(__name__)


class USOSymmetricTightSignalDetector(BaseSignalDetector):
    """USO 回檔 + Williams %R 訊號偵測器（同 USO-001）"""

    def __init__(self, config: USOSymmetricTightConfig):
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
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        df["Signal"] = cond_pullback & cond_wr

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
            logger.info("USO-005: %d signals suppressed by cooldown", len(suppressed))

        logger.info("USO-005: Detected %d Pullback+WR signals", df["Signal"].sum())
        return df

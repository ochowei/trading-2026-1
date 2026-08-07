"""TQQQ-012 QQQ confirmation detector for the execution-model slice."""

import logging

import pandas as pd

from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_012_cap_exec_qqq_confirm.config import (
    TQQQCapExecQqqConfirmConfig,
)

logger = logging.getLogger(__name__)


class TQQQCapExecQqqConfirmDetector(DeclaredAuxiliaryData, TQQQSignalDetector):
    """TQQQ capitulation detector with QQQ RSI confirmation."""

    def __init__(self, config: TQQQCapExecQqqConfirmConfig):
        super().__init__(config)
        self.qqq_config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.qqq_config.qqq_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().compute_indicators(df)
        df["QQQ_Close"] = self.require_auxiliary(self.qqq_config.qqq_ticker, df.index)["Close"]
        df["QQQ_RSI14"] = self._compute_rsi(df["QQQ_Close"], self.qqq_config.qqq_rsi_period)
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().detect_signals(df)
        qqq_mask = df["QQQ_RSI14"] < self.qqq_config.qqq_rsi_threshold
        original_count = df["Signal"].sum()
        df["Signal"] = df["Signal"] & qqq_mask
        filtered_count = df["Signal"].sum()
        suppressed = original_count - filtered_count
        if suppressed > 0:
            logger.info(
                "[TQQQCapExecQqqConfirmDetector] QQQ RSI filtered %s signals "
                "(threshold=%s, remaining=%s)",
                suppressed,
                self.qqq_config.qqq_rsi_threshold,
                filtered_count,
            )
        return df

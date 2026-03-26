"""
TQQQ + QQQ 相對強度確認訊號偵測模組 (TQQQ + QQQ Confirmation Signal Detector)
在原始三條件基礎上新增 QQQ RSI(14) < threshold 條件。
Adds QQQ RSI(14) < threshold condition on top of original 3-condition signal detection.
"""

import logging

import pandas as pd

from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_007_cap_qqq_confirm.config import TQQQCapQqqConfirmConfig

logger = logging.getLogger(__name__)


class TQQQCapQqqConfirmDetector(TQQQSignalDetector):
    """TQQQ + QQQ 相對強度確認訊號偵測器"""

    def __init__(self, config: TQQQCapQqqConfirmConfig):
        super().__init__(config)
        self.qqq_config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """先計算基線指標，再計算 QQQ RSI(14)。"""
        df = super().compute_indicators(df)

        if "QQQ_Close" not in df.columns:
            logger.warning(
                "[TQQQCapQqqConfirmDetector] DataFrame 中無 QQQ_Close 欄位，QQQ RSI 過濾將被跳過 "
                "(No QQQ_Close found, QQQ RSI filter will be skipped)"
            )
            return df

        df["QQQ_RSI14"] = self._compute_rsi(df["QQQ_Close"], self.qqq_config.qqq_rsi_period)
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號：原始三條件 + QQQ RSI 過濾。"""
        df = super().detect_signals(df)

        if "QQQ_RSI14" not in df.columns:
            logger.warning(
                "[TQQQCapQqqConfirmDetector] DataFrame 中無 QQQ_RSI14 欄位，跳過 QQQ RSI 過濾 "
                "(No QQQ_RSI14 found, skipping QQQ RSI filter)"
            )
            return df

        qqq_mask = df["QQQ_RSI14"] < self.qqq_config.qqq_rsi_threshold
        original_count = df["Signal"].sum()
        df["Signal"] = df["Signal"] & qqq_mask
        filtered_count = df["Signal"].sum()

        suppressed = original_count - filtered_count
        if suppressed > 0:
            logger.info(
                f"[TQQQCapQqqConfirmDetector] QQQ RSI 過濾抑制了 {suppressed} 個訊號 "
                f"(QQQ RSI >= {self.qqq_config.qqq_rsi_threshold}), "
                f"剩餘 {filtered_count} 個 ({suppressed} signals filtered, {filtered_count} remaining)"
            )

        return df

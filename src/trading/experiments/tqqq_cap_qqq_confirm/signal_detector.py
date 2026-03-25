"""
TQQQ QQQ 確認訊號偵測模組 (TQQQ Capitulation QQQ Confirm Signal Detector)
在原始三條件基礎上新增 QQQ RSI(14) < 35 條件。
Adds QQQ RSI < 35 condition on top of the original 3-condition signal detection.
"""

import logging
import pandas as pd

from trading.experiments.tqqq_cap_qqq_confirm.config import TQQQCapQqqConfirmConfig
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector

logger = logging.getLogger(__name__)


class TQQQCapQqqConfirmDetector(TQQQSignalDetector):
    """
    TQQQ QQQ 確認訊號偵測器
    """

    def __init__(self, config: TQQQCapQqqConfirmConfig):
        super().__init__(config)
        self.qqq_config = config

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號：原始三條件 + QQQ RSI 過濾"""
        # 先用原始邏輯偵測（含冷卻機制）
        df = super().detect_signals(df)

        # 若 DataFrame 中沒有 QQQ_RSI 欄位，直接返回（不做過濾）
        if "QQQ_RSI" not in df.columns:
            logger.warning(
                "[TQQQCapQqqConfirmDetector] DataFrame 中無 QQQ_RSI 欄位，跳過 QQQ RSI 過濾 "
                "(No QQQ_RSI column found, skipping QQQ RSI filter)"
            )
            return df

        # 新增 QQQ RSI 過濾條件
        qqq_rsi_mask = df["QQQ_RSI"] < self.qqq_config.qqq_rsi_threshold
        original_count = df["Signal"].sum()
        df["Signal"] = df["Signal"] & qqq_rsi_mask
        filtered_count = df["Signal"].sum()

        suppressed = original_count - filtered_count
        if suppressed > 0:
            logger.info(
                f"[TQQQCapQqqConfirmDetector] QQQ RSI 過濾抑制了 {suppressed} 個訊號 "
                f"(QQQ_RSI >= {self.qqq_config.qqq_rsi_threshold}), "
                f"剩餘 {filtered_count} 個 ({suppressed} signals filtered, {filtered_count} remaining)"
            )

        return df

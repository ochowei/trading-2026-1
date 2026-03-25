"""
TQQQ VIX 適應性訊號偵測模組 (TQQQ VIX Adaptive Signal Detector)
在原始三條件基礎上新增 VIX >= threshold 條件。
Adds VIX >= threshold condition on top of the original 3-condition signal detection.
"""

import logging

import pandas as pd

from trading.experiments.tqqq_cap_vix_adaptive.config import TQQQCapVixAdaptiveConfig
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector

logger = logging.getLogger(__name__)


class TQQQCapVixAdaptiveDetector(TQQQSignalDetector):
    """
    TQQQ VIX 適應性訊號偵測器 (TQQQ VIX Adaptive Signal Detector)

    四個條件同時成立時觸發訊號 (Signal triggers when all 4 conditions are met):
    1. 從 N 日高點回撤 >= threshold
    2. RSI(period) < threshold
    3. 成交量 > multiplier x 均量
    4. VIX >= vix_threshold (軟性過濾)
    """

    def __init__(self, config: TQQQCapVixAdaptiveConfig):
        super().__init__(config)
        self.vix_config = config

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號：原始三條件 + VIX 軟性過濾"""
        # 先用原始邏輯偵測（含冷卻機制）
        df = super().detect_signals(df)

        # 若 DataFrame 中沒有 VIX 欄位，直接返回（不做過濾）
        if "VIX" not in df.columns:
            logger.warning(
                "[TQQQCapVixAdaptiveDetector] DataFrame 中無 VIX 欄位，跳過 VIX 過濾 "
                "(No VIX column found, skipping VIX filter)"
            )
            return df

        # 新增 VIX 軟性過濾條件 (>= threshold)
        vix_mask = df["VIX"] >= self.vix_config.vix_threshold
        original_count = df["Signal"].sum()
        df["Signal"] = df["Signal"] & vix_mask
        filtered_count = df["Signal"].sum()

        suppressed = original_count - filtered_count
        if suppressed > 0:
            logger.info(
                f"[TQQQCapVixAdaptiveDetector] VIX 過濾抑制了 {suppressed} 個訊號 "
                f"(VIX < {self.vix_config.vix_threshold}), "
                f"剩餘 {filtered_count} 個 ({suppressed} signals filtered, {filtered_count} remaining)"
            )

        return df

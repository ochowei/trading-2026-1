"""
TQQQ VIX 軟性過濾訊號偵測模組 (TQQQ Soft VIX Filter Signal Detector)
在原始三條件基礎上新增 VIX >= 20 條件。
"""

import logging
import pandas as pd

from trading.experiments.tqqq_cap_vix_adaptive.config import TQQQCapVixAdaptiveConfig
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector

logger = logging.getLogger(__name__)


class TQQQCapVixAdaptiveDetector(TQQQSignalDetector):
    """
    TQQQ VIX 軟性過濾訊號偵測器
    """

    def __init__(self, config: TQQQCapVixAdaptiveConfig):
        super().__init__(config)
        self.vix_config = config

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號：原始三條件 + 軟性 VIX 過濾"""
        # 先用原始邏輯偵測（含冷卻機制）
        df = super().detect_signals(df)

        # 若 DataFrame 中沒有 VIX 欄位，直接返回（不做過濾）
        if "VIX" not in df.columns:
            logger.warning(
                "[TQQQCapVixAdaptiveDetector] DataFrame 中無 VIX 欄位，跳過 VIX 過濾 "
                "(No VIX column found, skipping VIX filter)"
            )
            return df

        # 新增 VIX 過濾條件 (VIX >= threshold)
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

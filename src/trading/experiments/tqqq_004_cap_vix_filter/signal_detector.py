"""
TQQQ VIX 過濾訊號偵測模組 (TQQQ VIX Filter Signal Detector)
在原始三條件基礎上新增 VIX > threshold 條件。
Adds VIX > threshold condition on top of the original 3-condition signal detection.
"""

import logging

import pandas as pd

from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_004_cap_vix_filter.config import TQQQCapVixFilterConfig

logger = logging.getLogger(__name__)


class TQQQCapVixFilterDetector(DeclaredAuxiliaryData, TQQQSignalDetector):
    """
    TQQQ VIX 過濾訊號偵測器 (TQQQ VIX Filter Signal Detector)

    四個條件同時成立時觸發訊號 (Signal triggers when all 4 conditions are met):
    1. 從 N 日高點回撤 ≥ threshold
    2. RSI(period) < threshold
    3. 成交量 > multiplier x 均量
    4. VIX > vix_threshold (新增)
    """

    def __init__(self, config: TQQQCapVixFilterConfig):
        super().__init__(config)
        self.vix_config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.vix_config.vix_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().compute_indicators(df)
        df["VIX"] = self.require_auxiliary(self.vix_config.vix_ticker, df.index)["Close"]
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號：原始三條件 + VIX 過濾"""
        # 先用原始邏輯偵測（含冷卻機制）
        df = super().detect_signals(df)

        # 新增 VIX 過濾條件
        vix_mask = df["VIX"] > self.vix_config.vix_threshold
        original_count = df["Signal"].sum()
        df["Signal"] = df["Signal"] & vix_mask
        filtered_count = df["Signal"].sum()

        suppressed = original_count - filtered_count
        if suppressed > 0:
            logger.info(
                f"[TQQQCapVixFilterDetector] VIX 過濾抑制了 {suppressed} 個訊號 "
                f"(VIX < {self.vix_config.vix_threshold}), "
                f"剩餘 {filtered_count} 個 ({suppressed} signals filtered, {filtered_count} remaining)"
            )

        return df

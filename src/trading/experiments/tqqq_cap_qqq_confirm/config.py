"""
TQQQ QQQ 確認策略配置 (TQQQ Capitulation QQQ Confirm Configuration)
在原始三條件基礎上新增 QQQ RSI 過濾，確保底層指數也處於超賣狀態。
Adds QQQ RSI < 35 condition on top of the original 3 conditions.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapQqqConfirmConfig(TQQQConfig):
    """TQQQ QQQ 確認策略配置"""

    # QQQ 過濾參數 (QQQ filter parameters)
    qqq_ticker: str = "QQQ"
    qqq_rsi_period: int = 14
    qqq_rsi_threshold: float = 35.0

    # 調整的出場條件
    profit_target: float = 0.06
    holding_days: int = 8


def create_default_config() -> TQQQCapQqqConfirmConfig:
    """建立預設 QQQ 確認配置"""
    return TQQQCapQqqConfirmConfig(
        name="tqqq_cap_qqq_confirm",
        experiment_id="TQQQ-007",
        display_name="TQQQ QQQ 確認策略 — Capitulation + QQQ Confirm",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        stop_loss=-0.08,
    )

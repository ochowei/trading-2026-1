"""
SOXL 反轉確認均值回歸策略配置
SOXL Reversal Confirm Mean Reversion Configuration

基於 SOXL-003，以 ClosePos 反轉確認取代成交量過濾，
過濾落刀型進場（close 接近當日最低），提升勝率。
3 次嘗試均未超越 SOXL-003 的 A/B 平衡表現。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLReversalConfirmConfig(ExperimentConfig):
    """SOXL 反轉確認策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25%（同 SOXL-003）
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    close_position_min: float = 0.35  # 收盤位置 ≥ 35%（反轉確認）

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 7

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLReversalConfirmConfig:
    """建立預設 SOXL-004 配置"""
    return SOXLReversalConfirmConfig(
        name="soxl_004_reversal_confirm",
        experiment_id="SOXL-004",
        display_name="SOXL 反轉確認 + 成交模型 — Reversal Confirm + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%（同 SOXL-003 甜蜜點）
        stop_loss=-0.12,  # -12%（同 SOXL-003）
        holding_days=20,  # 20 天（同 SOXL-003）
    )

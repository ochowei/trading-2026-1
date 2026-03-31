"""
SOXL 優化出場 + 成交模型配置
SOXL Optimized Exit + Execution Model Configuration

基於 SOXL-005，嘗試調整持倉天數與冷卻期以減少到期虧損。
三次嘗試均未能超越 SOXL-005。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXL006Config(ExperimentConfig):
    """SOXL-006 策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25% 下限
    drawdown_cap: float = -0.40  # -40% 上限（過濾極端崩盤）
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    drop_2d_threshold: float = -0.08  # 2日跌幅 ≤ -8%

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 10  # Att1: 7→10 天

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXL006Config:
    """建立預設 SOXL-006 配置（Attempt 1 版本）"""
    return SOXL006Config(
        name="soxl_006_optimized_exit",
        experiment_id="SOXL-006",
        display_name="SOXL 優化出場 + 成交模型 — Optimized Exit + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%
        stop_loss=-0.12,  # -12%
        holding_days=15,  # Att1: 20→15 天
    )

"""
SOXL 回撤範圍限制策略配置
SOXL Capped Drawdown Mean Reversion Configuration

基於 SOXL-003，加入回撤上限過濾極端崩盤訊號，
並以 2 日跌幅取代成交量過濾。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLCappedDrawdownConfig(ExperimentConfig):
    """SOXL 回撤範圍限制策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25% 下限
    drawdown_cap: float = -0.40  # -40% 上限（過濾極端崩盤）
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    drop_2d_threshold: float = -0.08  # 2日跌幅 ≤ -8%（取代成交量過濾）

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 7

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLCappedDrawdownConfig:
    """建立預設 SOXL-005 配置"""
    return SOXLCappedDrawdownConfig(
        name="soxl_005_capped_drawdown",
        experiment_id="SOXL-005",
        display_name="SOXL 回撤範圍限制 + 成交模型 — Capped Drawdown + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%（SOXL 甜蜜點）
        stop_loss=-0.12,  # -12%
        holding_days=20,  # 20 天
    )

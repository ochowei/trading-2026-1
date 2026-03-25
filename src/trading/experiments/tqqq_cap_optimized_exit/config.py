"""
TQQQ 優化出場策略配置 (TQQQ Optimized Exit Strategy Configuration)
保持基線進場條件不變，僅優化出場參數：獲利目標 +7%、持倉 10 天、無追蹤停利。
Keeps baseline entry conditions unchanged; optimizes exit: +7% target, 10-day hold, no trailing stop.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapOptimizedExitConfig(TQQQConfig):
    """TQQQ 優化出場策略配置"""

    # 優化的出場參數 (Optimized exit parameters)
    profit_target: float = 0.07   # +5% -> +7%
    holding_days: int = 10        # 7 -> 10


def create_default_config() -> TQQQCapOptimizedExitConfig:
    """建立預設優化出場配置 (Create default optimized exit config)"""
    return TQQQCapOptimizedExitConfig(
        name="tqqq_cap_optimized_exit",
        experiment_id="TQQQ-008",
        display_name="TQQQ 優化出場策略 — Optimized Exit Strategy",
        tags=["tqqq", "capitulation", "optimized_exit"],
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )

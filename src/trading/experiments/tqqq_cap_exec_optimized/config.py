"""
TQQQ 優化出場 + 成交模型配置 (TQQQ Optimized Exit + Execution Model Configuration)
重做 TQQQ-008：保持基線三條件進場 + 優化出場（+7%、10 天、無追蹤停利），新增成交模型。
Redo of TQQQ-008: Baseline 3-condition entry + optimized exit (+7%, 10d, no trailing), with execution model.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapExecOptimizedConfig(TQQQConfig):
    """TQQQ 優化出場 + 成交模型配置"""

    # 優化的出場參數 — 與 TQQQ-008 相同 (Same exit params as TQQQ-008)
    profit_target: float = 0.07   # +7%
    holding_days: int = 10        # 10 天

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001   # 0.1%


def create_default_config() -> TQQQCapExecOptimizedConfig:
    """建立預設配置 (Create default config)"""
    return TQQQCapExecOptimizedConfig(
        name="tqqq_cap_exec_optimized",
        experiment_id="TQQQ-010",
        display_name="TQQQ 優化出場 + 成交模型 — Optimized Exit + Execution Model",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )

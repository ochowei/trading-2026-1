"""
TQQQ 基線恐慌抄底 + 成交模型配置 (TQQQ Baseline Capitulation + Execution Model Configuration)
重做 TQQQ-001：三條件恐慌抄底 + 基礎出場（+5%、-8%、7 天），新增成交模型。
Redo of TQQQ-001: 3-condition capitulation entry + basic exit (+5%, -8%, 7d), with execution model.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapExecBaselineConfig(TQQQConfig):
    """TQQQ 基線恐慌抄底 + 成交模型配置"""

    # 出場參數 — 與 TQQQ-001 相同 (Same exit params as TQQQ-001)
    profit_target: float = 0.05   # +5%
    stop_loss: float = -0.08      # -8%
    holding_days: int = 7         # 7 天

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001   # 0.1%


def create_default_config() -> TQQQCapExecBaselineConfig:
    """建立預設配置 (Create default config)"""
    return TQQQCapExecBaselineConfig(
        name="tqqq_cap_exec_baseline",
        experiment_id="TQQQ-011",
        display_name="TQQQ 基線恐慌抄底 + 成交模型 — Baseline Capitulation + Execution Model",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )

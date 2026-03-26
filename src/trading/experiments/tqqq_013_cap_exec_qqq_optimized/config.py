"""
TQQQ QQQ 相對強度確認 + 優化出場 + 成交模型配置
(TQQQ QQQ Confirmation + Optimized Exit + Execution Model Configuration)

結合 TQQQ-012 的 QQQ RSI 過濾與 TQQQ-010 的優化出場參數，
並維持成交模型（隔日開盤進場、限價止盈、停損市價、悲觀認定）。
Combines TQQQ-012's QQQ filter with TQQQ-010's optimized exits,
under the same realistic execution model.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_007_cap_qqq_confirm.config import TQQQCapQqqConfirmConfig


@dataclass
class TQQQCapExecQqqOptimizedConfig(TQQQCapQqqConfirmConfig):
    """TQQQ QQQ 確認 + 優化出場 + 成交模型配置"""

    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQCapExecQqqOptimizedConfig:
    """建立預設配置 (Create default config)"""
    return TQQQCapExecQqqOptimizedConfig(
        name="tqqq_013_cap_exec_qqq_optimized",
        experiment_id="TQQQ-013",
        display_name="TQQQ QQQ 確認 + 優化出場 + 成交模型 — QQQ Confirm + Optimized Exit + Execution Model",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        # 承襲 TQQQ-010 的優化出場
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
        cooldown_days=3,
        # 承襲 TQQQ-007/TQQQ-012 的 QQQ RSI 過濾
        qqq_rsi_period=14,
        qqq_rsi_threshold=35.0,
    )

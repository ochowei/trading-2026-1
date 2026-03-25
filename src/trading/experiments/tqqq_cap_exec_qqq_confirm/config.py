"""
TQQQ QQQ 相對強度確認 + 成交模型配置 (TQQQ QQQ Confirmation + Execution Model Configuration)
重做 TQQQ-007：基線恐慌 + QQQ RSI(14)<35 過濾 + 出場（+6%、-8%、8 天），新增成交模型。
Redo of TQQQ-007: Baseline capitulation + QQQ RSI(14)<35 filter + exit (+6%, -8%, 8d), with execution model.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_cap_qqq_confirm.config import TQQQCapQqqConfirmConfig


@dataclass
class TQQQCapExecQqqConfirmConfig(TQQQCapQqqConfirmConfig):
    """TQQQ QQQ 確認 + 成交模型配置"""

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001   # 0.1%


def create_default_config() -> TQQQCapExecQqqConfirmConfig:
    """建立預設配置 (Create default config)"""
    return TQQQCapExecQqqConfirmConfig(
        name="tqqq_cap_exec_qqq_confirm",
        experiment_id="TQQQ-012",
        display_name="TQQQ QQQ 確認 + 成交模型 — QQQ Confirm + Execution Model",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.06,
        stop_loss=-0.08,
        holding_days=8,
        cooldown_days=3,
    )

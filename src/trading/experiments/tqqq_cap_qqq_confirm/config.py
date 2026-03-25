"""
TQQQ + QQQ 相對強度確認策略配置 (TQQQ + QQQ Confirmation Strategy Configuration)
在基線恐慌訊號上加入 QQQ RSI(14) < 35，過濾僅屬於槓桿放大的假恐慌。
Adds QQQ RSI(14) < 35 on top of baseline capitulation signals to filter leverage-only pseudo panics.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapQqqConfirmConfig(TQQQConfig):
    """TQQQ + QQQ 相對強度確認策略配置"""

    qqq_ticker: str = "QQQ"         # 底層指數 ETF
    qqq_rsi_period: int = 14         # QQQ RSI 週期
    qqq_rsi_threshold: float = 35.0  # QQQ RSI 必須低於此值


def create_default_config() -> TQQQCapQqqConfirmConfig:
    """建立預設 QQQ 確認配置 (Create default QQQ confirmation config)"""
    return TQQQCapQqqConfirmConfig(
        name="tqqq_cap_qqq_confirm",
        experiment_id="TQQQ-007",
        display_name="TQQQ QQQ 相對強度確認策略 — Capitulation + QQQ RSI Confirm",
        tags=["tqqq", "capitulation", "qqq_confirm"],
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

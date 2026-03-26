"""
TQQQ 加寬出場策略配置 (TQQQ Wider Exit Strategy Configuration)
加寬獲利目標至 +12%，新增追蹤停利機制。
Widens profit target to +12% and adds a trailing stop mechanism.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class TQQQCapWiderExitConfig(TQQQConfig):
    """TQQQ 加寬出場策略配置"""

    # 加寬的獲利目標與持倉天數 (Wider profit target and holding period)
    profit_target: float = 0.12  # +5% -> +12%
    holding_days: int = 12  # 7 -> 12

    # 追蹤停利 (Trailing stop from peak close since entry)
    trailing_stop_pct: float = -0.04  # 從持倉期間最高收盤價回落 4% 即出場


def create_default_config() -> TQQQCapWiderExitConfig:
    """建立預設加寬出場配置 (Create default wider exit config)"""
    return TQQQCapWiderExitConfig(
        name="tqqq_003_cap_wider_exit",
        experiment_id="TQQQ-003",
        display_name="TQQQ 加寬出場策略 — Wider Exit with Trailing Stop",
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

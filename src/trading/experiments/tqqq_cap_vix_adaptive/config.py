"""
TQQQ VIX 適應性策略配置 (TQQQ VIX Adaptive Strategy Configuration)
軟性 VIX + 適應性出場：VIX >= 20，獲利目標 +8%，追蹤停利 -6%，持倉 10 天。
Soft VIX + Adaptive Exit: VIX >= 20, +8% profit target, -6% trailing stop, 10 days holding.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapVixAdaptiveConfig(TQQQConfig):
    """TQQQ VIX 適應性策略配置"""

    # VIX 過濾參數 (VIX filter parameters)
    vix_ticker: str = "^VIX"            # VIX 標的代碼
    vix_threshold: float = 20.0         # VIX 必須高於此值才觸發訊號 (TQQQ-004: 25.0)

    # 適應性出場參數 (Adaptive exit parameters)
    profit_target: float = 0.08         # 獲利目標 (TQQQ-001: 0.05, TQQQ-003: 0.12)
    trailing_stop_pct: float = -0.06    # 追蹤停利從最高收盤回落比例 (TQQQ-003: -0.04)
    holding_days: int = 10              # 持倉天數 (TQQQ-001: 7)
    stop_loss: float = -0.08            # 停損 (維持不變)


def create_default_config() -> TQQQCapVixAdaptiveConfig:
    """建立預設 VIX 適應性配置 (Create default VIX adaptive config)"""
    return TQQQCapVixAdaptiveConfig(
        name="tqqq_cap_vix_adaptive",
        experiment_id="TQQQ-005",
        display_name="TQQQ 軟性VIX與適應性出場策略 — Capitulation + Soft VIX + Adaptive Exit",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.08,
        stop_loss=-0.08,
        holding_days=10,
    )

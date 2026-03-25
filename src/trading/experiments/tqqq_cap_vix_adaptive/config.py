"""
TQQQ VIX 軟性過濾 + 適應性出場策略配置
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapVixAdaptiveConfig(TQQQConfig):
    """TQQQ VIX 軟性過濾 + 適應性出場策略配置"""

    # VIX 軟性過濾參數 (Soft VIX filter parameters)
    vix_ticker: str = "^VIX"            # VIX 標的代碼
    vix_threshold: float = 20.0         # VIX 必須高於此值才觸發訊號 (原 TQQQ-004 為 25.0)

    # 適應性出場參數 (Adaptive exit parameters)
    profit_target: float = 0.08         # 獲利目標提高至 +8% (原基線為 +5%)
    trailing_stop_pct: float = -0.06    # 追蹤停利放寬至 -6% (原 TQQQ-003 為 -4%)
    holding_days: int = 10              # 持倉天數延長至 10 天 (原基線為 7 天)


def create_default_config() -> TQQQCapVixAdaptiveConfig:
    """建立預設 VIX 軟性過濾 + 適應性出場配置"""
    return TQQQCapVixAdaptiveConfig(
        name="tqqq_cap_vix_adaptive",
        experiment_id="TQQQ-005",
        display_name="TQQQ 軟性 VIX + 適應性出場 — Soft VIX Filter & Adaptive Exit",
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

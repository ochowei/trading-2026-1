"""
TQQQ 軟性 VIX + 適應性出場策略配置 (TQQQ Soft VIX + Adaptive Exit Configuration)
以 VIX >= 20 過濾低恐慌訊號，並搭配較寬鬆的出場機制。
Filters low-fear signals with VIX >= 20 and applies wider/adaptive exit logic.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_cap_wider_exit.config import TQQQCapWiderExitConfig


@dataclass
class TQQQCapVixAdaptiveConfig(TQQQCapWiderExitConfig):
    """TQQQ 軟性 VIX + 適應性出場策略配置"""

    # VIX 過濾參數 (VIX filter parameters)
    vix_ticker: str = "^VIX"            # VIX 標的代碼
    vix_threshold: float = 20.0         # VIX 必須高於此值才觸發訊號



def create_default_config() -> TQQQCapVixAdaptiveConfig:
    """建立預設軟性 VIX + 適應性出場配置 (Create default config)"""
    return TQQQCapVixAdaptiveConfig(
        name="tqqq_cap_vix_adaptive",
        experiment_id="TQQQ-005",
        display_name="TQQQ 軟性 VIX + 適應性出場策略 — Soft VIX + Adaptive Exit",
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
        trailing_stop_pct=-0.06,
    )

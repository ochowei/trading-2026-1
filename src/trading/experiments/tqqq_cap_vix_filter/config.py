"""
TQQQ VIX 過濾策略配置 (TQQQ VIX Filter Strategy Configuration)
在原始三條件基礎上新增 VIX 恐慌門檻，只在市場真正恐慌時進場。
Adds a VIX fear threshold on top of the original 3 conditions, entering only during genuine market panic.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapVixFilterConfig(TQQQConfig):
    """TQQQ VIX 過濾策略配置"""

    # VIX 過濾參數 (VIX filter parameters)
    vix_ticker: str = "^VIX"            # VIX 標的代碼
    vix_threshold: float = 25.0         # VIX 必須高於此值才觸發訊號


def create_default_config() -> TQQQCapVixFilterConfig:
    """建立預設 VIX 過濾配置 (Create default VIX filter config)"""
    return TQQQCapVixFilterConfig(
        name="tqqq_cap_vix_filter",
        display_name="TQQQ VIX 過濾策略 — VIX Regime Filter Strategy",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,
        stop_loss=-0.08,
        holding_days=7,
    )

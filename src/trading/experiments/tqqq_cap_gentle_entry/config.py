"""
TQQQ 溫和放寬進場策略配置 (TQQQ Gentle Entry Relaxation Configuration)
僅溫和放寬 drawdown 門檻（-15% → -13%），保持 RSI/Volume 嚴格不變，
搭配 TQQQ-008 的優化出場參數。
Only gently relaxes drawdown threshold (-15% -> -13%), keeps RSI/Volume strict,
combined with TQQQ-008's optimized exit parameters.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_capitulation.config import TQQQConfig


@dataclass
class TQQQCapGentleEntryConfig(TQQQConfig):
    """TQQQ 溫和放寬進場策略配置"""

    # 溫和放寬的進場閾值（僅 drawdown）(Gently relaxed entry - drawdown only)
    drawdown_threshold: float = -0.13   # -15% -> -13%

    # RSI 和 Volume 保持基線嚴格值不變
    # rsi_threshold: float = 25.0       # 不變 (unchanged)
    # volume_multiplier: float = 1.5    # 不變 (unchanged)

    # 搭配 TQQQ-008 的優化出場參數 (TQQQ-008's optimized exit)
    profit_target: float = 0.07   # +5% -> +7%
    holding_days: int = 10        # 7 -> 10


def create_default_config() -> TQQQCapGentleEntryConfig:
    """建立預設溫和放寬進場配置 (Create default gentle entry config)"""
    return TQQQCapGentleEntryConfig(
        name="tqqq_cap_gentle_entry",
        experiment_id="TQQQ-009",
        display_name="TQQQ 溫和放寬進場策略 — Gentle Entry Relaxation",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
    )

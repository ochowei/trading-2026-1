"""
IBIT-002: 回檔 + Williams %R 均值回歸（出場優化）
(IBIT Pullback + Williams %R Mean Reversion with Exit Optimization)

與 IBIT-001 同樣的進場條件（回檔 12-22% + WR(10) ≤ -80 + 冷卻 15 天），
測試 SL 收窄至 -6.0%（減少每筆停損損失 ~1%），持倉延長至 20 天。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBITRSI2PullbackConfig(ExperimentConfig):
    """IBIT 回檔 + WR 出場優化參數"""

    # 進場指標（同 IBIT-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 回檔 >= 12%
    pullback_upper: float = -0.22  # 回檔上限 22%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 15


def create_default_config() -> IBITRSI2PullbackConfig:
    return IBITRSI2PullbackConfig(
        name="ibit_002_rsi2_pullback",
        experiment_id="IBIT-002",
        display_name="IBIT Pullback + WR Exit Optimized",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,  # +5.0%（同 IBIT-001）
        stop_loss=-0.06,  # -6.0%（收窄自 -7.0%）
        holding_days=15,  # 15 天（同 IBIT-001）
    )

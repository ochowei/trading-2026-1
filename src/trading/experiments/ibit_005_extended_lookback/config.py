"""
IBIT-005: 均值回歸 SL -8% 出場優化配置
(IBIT Mean Reversion SL -8% Exit Optimization Config)

基於 IBIT-001 進場條件（回檔 12-22% + WR(10) ≤ -80），僅變更停損至 -8%。
IBIT 已測試 SL：-5.5%（過緊）、-6%（Feb26 翻轉）、-7%（最佳）、-9%（過寬）。
SL -8% 是唯一未測試的中間值。

Att1（失敗）: 20 日回看 + 20 日冷卻，Part B Sharpe -0.38
Att2（失敗）: 短期動量 5 日漲幅 > 10%，Part A 1.00 / Part B -0.55（市場狀態依賴）
Att3: IBIT-001 進場 + SL -8%（僅測試停損調整）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT005Config(ExperimentConfig):
    """IBIT-005 SL -8% 出場優化參數"""

    # 進場指標（同 IBIT-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 回檔 >= 12%
    pullback_upper: float = -0.22  # 回檔上限 22%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 15  # 冷卻 15 天（同 IBIT-001）


def create_default_config() -> IBIT005Config:
    return IBIT005Config(
        name="ibit_005_extended_lookback",
        experiment_id="IBIT-005",
        display_name="IBIT Mean Reversion SL -8%",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,  # +5.0%（同 IBIT-001）
        stop_loss=-0.08,  # -8.0%（唯一變更：-7% → -8%）
        holding_days=15,  # 15 天（同 IBIT-001）
    )

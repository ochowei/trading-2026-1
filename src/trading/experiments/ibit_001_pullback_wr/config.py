"""
IBIT-001: 回檔 + Williams %R 均值回歸配置
(IBIT Pullback + Williams %R Mean Reversion Config)

IBIT (iShares Bitcoin Trust ETF) 日波動度 ~3.17%，與 GLD 比率 2.64x。
參考 COPX-001 / URA-001 回檔範圍 + Williams %R 架構，按 IBIT 波動度縮放參數：
- 回檔範圍：12-22%（過濾淺回檔與極端崩盤）
- WR(10) <= -80（標準超賣門檻）
- TP +5.0%（快速獲利了結，加密 ETF 反彈速度快）
- SL -7.0%（非對稱寬停損）
- 冷卻 15 天（避免下跌趨勢中連續進場）
- 不使用追蹤停損（日波動 3.17% 禁用區域）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBITPullbackWRConfig(ExperimentConfig):
    """IBIT 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 回檔 >= 12%
    pullback_upper: float = -0.22  # 回檔上限 22%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80 (超賣)
    cooldown_days: int = 15


def create_default_config() -> IBITPullbackWRConfig:
    return IBITPullbackWRConfig(
        name="ibit_001_pullback_wr",
        experiment_id="IBIT-001",
        display_name="IBIT Pullback + Williams %R Mean Reversion",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,  # +5.0%
        stop_loss=-0.07,  # -7.0%（非對稱寬停損）
        holding_days=15,  # 15 天
    )

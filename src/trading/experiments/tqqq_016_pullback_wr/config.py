"""
TQQQ-016: 回檔 + Williams %R 均值回歸配置
(TQQQ Pullback + Williams %R Mean Reversion Config)

TQQQ (ProShares UltraPro QQQ) 3x 槓桿 ETF，日波動度 ~5%。
使用 pullback+WR+Volume 框架（結合多資產成功的均值回歸模式 + TQQQ-010 的恐慌過濾），
按 TQQQ 波動度縮放參數：
- 回檔範圍：18-30%（過濾淺回檔與極端崩盤）
- WR(10) <= -80（超賣確認）
- 成交量 > 1.5x 20日均量（恐慌賣壓確認）
- TP +7.0% / SL -8.0%（沿用 TQQQ-010 已驗證最佳出場）
- 冷卻 10 天（防止下跌趨勢中連續進場）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQPullbackWRConfig(ExperimentConfig):
    """TQQQ 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.18  # 回檔 >= 18%
    pullback_upper: float = -0.30  # 回檔上限 30%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80 (超賣)
    volume_multiplier: float = 1.5  # 成交量 > 1.5x 均量（恐慌過濾）
    volume_sma_period: int = 20
    cooldown_days: int = 10

    # 成交模型參數
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQPullbackWRConfig:
    return TQQQPullbackWRConfig(
        name="tqqq_016_pullback_wr",
        experiment_id="TQQQ-016",
        display_name="TQQQ Pullback + Williams %R Mean Reversion",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,  # +7.0%（TQQQ-010 已驗證最佳）
        stop_loss=-0.08,  # -8.0%（TQQQ-010 已驗證最佳）
        holding_days=10,  # 10 天（TQQQ-010 已驗證最佳）
    )

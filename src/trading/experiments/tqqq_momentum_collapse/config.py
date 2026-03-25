"""
TQQQ 多日動能崩潰策略配置 (TQQQ Multi-Day Momentum Collapse Configuration)
捕捉 TQQQ 連續多日緩慢洗盤的底部形態。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQMomentumCollapseConfig(ExperimentConfig):
    """TQQQ 多日動能崩潰策略配置"""

    # 動能崩潰參數
    momentum_lookback: int = 5           # 觀察過去 5 天
    negative_days_threshold: int = 4     # 至少 4 天收盤下跌
    return_threshold: float = -0.12      # 5 日累計報酬 <= -12%
    sma_period: int = 50                 # 收盤價 < 50 日 SMA

    # 出場參數
    profit_target: float = 0.07          # 獲利目標 +7%
    stop_loss: float = -0.10             # 停損 -10% (風險較高，停損較寬)
    holding_days: int = 10               # 最長持倉 10 天
    cooldown_days: int = 5               # 冷卻期 5 天


def create_default_config() -> TQQQMomentumCollapseConfig:
    """建立預設多日動能崩潰配置"""
    return TQQQMomentumCollapseConfig(
        name="tqqq_momentum_collapse",
        experiment_id="TQQQ-006",
        display_name="TQQQ 多日動能崩潰策略 — Multi-Day Momentum Collapse",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.10,
        holding_days=10,
    )

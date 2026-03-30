"""
TSLA 極端超賣均值回歸策略配置
TSLA Extreme Oversold Mean Reversion Configuration
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAExtremeOversoldConfig(ExperimentConfig):
    """TSLA 極端超賣策略專屬參數"""

    # 回撤條件：收盤價低於 N 日高點的幅度（範圍過濾）
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.20  # 低於 60 日高點 20%（下限）
    drawdown_upper: float = -0.45  # 不超過 45%（上限，過濾極端崩盤）

    # RSI(2) 極端短期超賣
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15

    # 2日急跌幅度
    two_day_drop: float = -0.06  # 2日跌幅 >= 6%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> TSLAExtremeOversoldConfig:
    """建立預設配置"""
    return TSLAExtremeOversoldConfig(
        name="tsla_001_extreme_oversold",
        experiment_id="TSLA-001",
        display_name="TSLA Extreme Oversold Mean Reversion",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,  # +10% 獲利目標
        stop_loss=-0.15,  # -15% 停損（TSLA 高波動需寬 SL）
        holding_days=15,  # 15 天持倉（短期反彈）
    )

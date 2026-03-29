"""
NVDA 極端超賣均值回歸策略配置
NVDA Extreme Oversold Mean Reversion Configuration
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDAExtremeOversoldConfig(ExperimentConfig):
    """NVDA 極端超賣策略專屬參數"""

    # RSI(2) 條件
    rsi_period: int = 2
    rsi_threshold: float = 5.0  # RSI(2) < 5（極端超賣）

    # 2日急跌條件
    drop_2d_threshold: float = -0.07  # 2日累計跌幅 >= 7%

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> NVDAExtremeOversoldConfig:
    """建立預設配置"""
    return NVDAExtremeOversoldConfig(
        name="nvda_001_extreme_oversold",
        experiment_id="NVDA-001",
        display_name="NVDA Extreme Oversold Mean Reversion",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,  # +8% 獲利目標
        stop_loss=-0.10,  # -10% 停損（非對稱，給波動空間）
        holding_days=15,  # 15 天持倉
    )

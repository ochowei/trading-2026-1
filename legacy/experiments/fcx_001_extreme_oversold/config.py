"""
FCX 極端超賣均值回歸策略配置
FCX Extreme Oversold Mean Reversion Configuration
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXExtremeOversoldConfig(ExperimentConfig):
    """FCX 極端超賣策略專屬參數"""

    # 回撤條件：收盤價低於 N 日高點的幅度
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.18  # 低於 60 日高點 18%

    # RSI 條件
    rsi_period: int = 10
    rsi_threshold: float = 28.0  # RSI(10) < 28

    # SMA 乖離條件
    sma_period: int = 50
    sma_deviation_threshold: float = -0.08  # 收盤價低於 SMA50 超過 8%

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> FCXExtremeOversoldConfig:
    """建立預設配置"""
    return FCXExtremeOversoldConfig(
        name="fcx_001_extreme_oversold",
        experiment_id="FCX-001",
        display_name="FCX Extreme Oversold Mean Reversion",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.10,  # +10% 獲利目標（銅礦反彈力道強）
        stop_loss=-0.12,  # -12% 停損（極端超賣給更多空間）
        holding_days=25,  # 25 天持倉
    )

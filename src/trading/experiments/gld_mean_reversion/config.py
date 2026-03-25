"""
GLD 均值回歸策略配置
"""

from dataclasses import dataclass
from trading.core.base_config import ExperimentConfig

@dataclass
class GLDMeanReversionConfig(ExperimentConfig):
    """GLD 均值回歸特定參數"""
    rsi_period: int = 10
    rsi_threshold: float = 30.0
    sma_period: int = 20
    sma_deviation_threshold: float = -0.015 # 跌破 20MA 至少 1.5%
    cooldown_days: int = 10

def create_default_config() -> GLDMeanReversionConfig:
    return GLDMeanReversionConfig(
        name="gld_mean_reversion",
        experiment_id="GLD-001",
        display_name="GLD Deep Oversold Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.015, # 1.5% profit target
        stop_loss=-0.03, # 3% stop loss
        holding_days=10, # 10 days holding period
    )

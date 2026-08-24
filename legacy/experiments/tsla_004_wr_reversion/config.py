"""
TSLA-004: Williams %R 均值回歸策略配置
TSLA Williams %R Mean Reversion Configuration

假說：高波動資產（日波動 3.72%）使用 WR(10) 比 RSI(2) 更穩定（跨資產教訓 #13）。
WR(10) 的 10 日回看提供更寬視角，在高波動環境下減少假訊號。
搭配 SL -13%（比 TSLA-002 的 -15% 收窄），因 WR 進場品質較高可承受較緊 SL。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAWRReversionConfig(ExperimentConfig):
    """TSLA WR 均值回歸策略專屬參數"""

    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.20
    drawdown_upper: float = -0.45
    wr_period: int = 10
    wr_threshold: float = -80.0
    two_day_drop: float = -0.06
    cooldown_days: int = 10


def create_default_config() -> TSLAWRReversionConfig:
    """建立預設配置"""
    return TSLAWRReversionConfig(
        name="tsla_004_wr_reversion",
        experiment_id="TSLA-004",
        display_name="TSLA Williams %R Mean Reversion",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.13,
        holding_days=25,
    )

"""
TSLA-003: 緊密回撤範圍均值回歸策略配置
TSLA Tight Retracement Mean Reversion Configuration

收窄回撤範圍至 [-40%, -22%]，過濾淺回調與極端崩盤。
提高 2日急跌門檻至 -7%，確認更強烈的恐慌拋售。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLATightRetracementConfig(ExperimentConfig):
    """TSLA 緊密回撤策略專屬參數"""

    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.22  # 收緊：從 -20% → -22%
    drawdown_upper: float = -0.40  # 收緊：從 -45% → -40%
    rsi_period: int = 2
    rsi_threshold: float = 15.0
    two_day_drop: float = -0.07  # 收緊：從 -6% → -7%
    cooldown_days: int = 10


def create_default_config() -> TSLATightRetracementConfig:
    """建立預設配置"""
    return TSLATightRetracementConfig(
        name="tsla_003_tight_retracement",
        experiment_id="TSLA-003",
        display_name="TSLA Tight Retracement Mean Reversion",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.15,
        holding_days=25,
    )

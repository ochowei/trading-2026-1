"""
TSLA-002: 寬出場均值回歸策略配置
TSLA Wider Exit Mean Reversion Configuration

與 TSLA-001 相同進場條件，但降低 TP（+7%）、延長持倉（25天）。
假說：TP +10% 過高（滾動窗口「差點成功」比例偏高），降低 TP 可捕捉更多反彈；
延長持倉讓到期交易有更多時間達標。SL 維持 -15%（已驗證的最佳值）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAWiderExitConfig(ExperimentConfig):
    """TSLA 寬出場策略專屬參數"""

    # 進場條件同 TSLA-001
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.20
    drawdown_upper: float = -0.45
    rsi_period: int = 2
    rsi_threshold: float = 15.0
    two_day_drop: float = -0.06
    cooldown_days: int = 10


def create_default_config() -> TSLAWiderExitConfig:
    """建立預設配置"""
    return TSLAWiderExitConfig(
        name="tsla_002_wider_exit",
        experiment_id="TSLA-002",
        display_name="TSLA Wider Exit Mean Reversion",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.07,  # +7%（降低 TP 捕捉更多反彈）
        stop_loss=-0.15,  # -15%（維持 TSLA-001 已驗證的 SL）
        holding_days=25,  # 25 天（延長持倉讓到期交易達標）
    )

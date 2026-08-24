"""
USO 回檔 + RSI(2) 極端超賣配置 (USO-007)

假設：RSI(2) < 15 比 WR(10) ≤ -80 更適合 USO 的短持倉特性（平均 2-3 天），
因為 RSI(2) 衡量的是 2 天內的超賣程度，與持倉週期更匹配。
進場回檔條件與出場參數沿用 USO-005。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOSharpPullbackConfig(ExperimentConfig):
    """USO 回檔 + RSI(2) 參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 回檔 ≥6%（同 USO-005）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    cooldown_days: int = 10


def create_default_config() -> USOSharpPullbackConfig:
    return USOSharpPullbackConfig(
        name="uso_007_sharp_pullback",
        experiment_id="USO-007",
        display_name="USO Pullback + RSI(2) Oversold",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.0325,
        holding_days=10,
    )

"""
TSLA-011: Breakout from Oversold Base Configuration

Hypothesis: TSLA is momentum-driven. When it makes a new 20-day high after having
been in deep pullback (-20%+), the breakout signals strong recovery momentum.
This avoids catching falling knives: during bear markets the stock rarely makes
new 20-day highs, so breakout signals are naturally filtered.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLABreakoutConfig(ExperimentConfig):
    """TSLA 突破策略專屬參數"""

    drawdown_lookback: int = 60
    pullback_lookback: int = 20
    pullback_threshold: float = -0.20
    breakout_lookback: int = 20
    cooldown_days: int = 20


def create_default_config() -> TSLABreakoutConfig:
    """建立預設配置"""
    return TSLABreakoutConfig(
        name="tsla_011_momentum_recovery",
        experiment_id="TSLA-011",
        display_name="TSLA Breakout from Oversold Base",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.10,
        holding_days=20,
    )

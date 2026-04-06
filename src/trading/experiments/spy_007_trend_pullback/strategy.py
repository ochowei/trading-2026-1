"""
SPY-007: Trend Pullback to SMA(50)
(SPY Trend Following Strategy)

使用 SMA 黃金交叉 + 回測 SMA(50) + 反彈作為順勢進場訊號，
搭配 ExecutionModelBacktester 成交模型。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_007_trend_pullback.config import (
    SPY007TrendPullbackConfig,
    create_default_config,
)
from trading.experiments.spy_007_trend_pullback.signal_detector import (
    SPY007TrendPullbackDetector,
)


class SPY007TrendPullbackStrategy(ExecutionModelStrategy):
    """SPY Trend Pullback to SMA(50) (SPY-007)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPY007TrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPY007TrendPullbackConfig):
            print(f"  SMA 短線: {config.sma_short_period}")
            print(f"  SMA 中線: {config.sma_mid_period}")
            print(f"  SMA 長線: {config.sma_long_period}")
            print(f"  收盤位置: >= {config.close_position_threshold:.0%} of day range")
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)

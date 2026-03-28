"""
USO 回檔 + RSI(2) 極端超賣策略 (USO-007)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_007_sharp_pullback.config import (
    USOSharpPullbackConfig,
    create_default_config,
)
from trading.experiments.uso_007_sharp_pullback.signal_detector import (
    USOSharpPullbackSignalDetector,
)


class USOSharpPullbackStrategy(ExecutionModelStrategy):
    """USO-007：回檔 + RSI(2) 極端超賣"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USOSharpPullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USOSharpPullbackConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

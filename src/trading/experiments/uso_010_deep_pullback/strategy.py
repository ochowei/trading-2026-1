"""
USO 深回檔 + RSI(2) + 2日急跌策略 (USO-010)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_010_deep_pullback.config import (
    USODeepPullbackConfig,
    create_default_config,
)
from trading.experiments.uso_010_deep_pullback.signal_detector import (
    USODeepPullbackSignalDetector,
)


class USODeepPullbackStrategy(ExecutionModelStrategy):
    """USO-010：深回檔 + RSI(2) + 2日急跌"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USODeepPullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USODeepPullbackConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日報酬 (2-Day Drop) <= {config.drop_2d_threshold:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

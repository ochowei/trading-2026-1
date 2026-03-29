"""
VOO-002: RSI(2) 非對稱出場均值回歸
(VOO RSI(2) Asymmetric Exit Mean Reversion)

套用 DIA-003 的非對稱出場策略：SL -3.5% / 20d。
Applies DIA-003's asymmetric exit: SL -3.5% / 20d.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_002_asymmetric_exit.config import (
    VOOAsymmetricConfig,
    create_default_config,
)
from trading.experiments.voo_002_asymmetric_exit.signal_detector import (
    VOOAsymmetricSignalDetector,
)


class VOOAsymmetricStrategy(ExecutionModelStrategy):
    """VOO RSI(2) 非對稱出場均值回歸 (VOO-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VOOAsymmetricSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VOOAsymmetricConfig):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

"""
VGK-003: RSI(2) Extended Hold Mean Reversion
(VGK RSI(2) 延長持倉均值回歸)

VGK-001 entry + DIA-005 exit optimization (SL -3.5%, hold 25d, cooldown 10d).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_003_extended_hold_rsi2.config import (
    VGK003Config,
    create_default_config,
)
from trading.experiments.vgk_003_extended_hold_rsi2.signal_detector import (
    VGK003SignalDetector,
)


class VGK003Strategy(ExecutionModelStrategy):
    """VGK RSI(2) 延長持倉均值回歸 (VGK-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK003Config):
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

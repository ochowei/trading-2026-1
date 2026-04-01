"""
DIA-005: RSI(2) 延長持倉均值回歸
(DIA RSI(2) Extended Holding Mean Reversion)

同 DIA-004 進場條件，延長持倉期至 25 天。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_005_extreme_entry.config import (
    DIAExtendedHoldConfig,
    create_default_config,
)
from trading.experiments.dia_005_extreme_entry.signal_detector import (
    DIAExtendedHoldSignalDetector,
)


class DIAExtendedHoldStrategy(ExecutionModelStrategy):
    """DIA RSI(2) 延長持倉均值回歸 (DIA-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIAExtendedHoldSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIAExtendedHoldConfig):
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

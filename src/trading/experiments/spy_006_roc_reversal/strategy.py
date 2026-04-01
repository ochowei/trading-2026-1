"""
SPY-006: RSI(2) 寬獲利目標均值回歸
(SPY RSI(2) Wider TP Mean Reversion)

使用同 SPY-005 進場條件搭配 TP +3.5% 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_006_roc_reversal.config import (
    SPYROCReversalConfig,
    create_default_config,
)
from trading.experiments.spy_006_roc_reversal.signal_detector import (
    SPYROCReversalSignalDetector,
)


class SPYROCReversalStrategy(ExecutionModelStrategy):
    """SPY RSI(2) 寬獲利目標均值回歸 (SPY-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPYROCReversalSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPYROCReversalConfig):
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

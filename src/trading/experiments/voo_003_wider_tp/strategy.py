"""
VOO-003: RSI(2) 寬獲利目標均值回歸
(VOO RSI(2) Wider TP Mean Reversion)

TP 從 +2.5% 提升至 +3.0%，與 SPY-005 對齊。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_003_wider_tp.config import (
    VOOWiderTPConfig,
    create_default_config,
)
from trading.experiments.voo_003_wider_tp.signal_detector import (
    VOOWiderTPSignalDetector,
)


class VOOWiderTPStrategy(ExecutionModelStrategy):
    """VOO RSI(2) 寬獲利目標均值回歸 (VOO-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VOOWiderTPSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VOOWiderTPConfig):
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

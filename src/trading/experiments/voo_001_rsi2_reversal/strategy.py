"""
VOO-001: RSI(2) 極端超賣均值回歸
(VOO RSI(2) Extreme Oversold Mean Reversion)

移植自 SPY-004，使用 RSI(2) 訊號架構搭配 ExecutionModelBacktester 固定 TP/SL 出場。
Ported from SPY-004, using RSI(2) signal framework with ExecutionModelBacktester fixed TP/SL exit.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_001_rsi2_reversal.config import (
    VOORsi2Config,
    create_default_config,
)
from trading.experiments.voo_001_rsi2_reversal.signal_detector import (
    VOORsi2SignalDetector,
)


class VOORsi2Strategy(ExecutionModelStrategy):
    """VOO RSI(2) 極端超賣均值回歸 (VOO-001)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VOORsi2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VOORsi2Config):
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

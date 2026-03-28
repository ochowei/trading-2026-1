"""
SPY-004: RSI(2) 極端超賣均值回歸
(SPY RSI(2) Extreme Oversold Mean Reversion)

使用 RSI(2) 訊號架構搭配 ExecutionModelBacktester 固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_004_rsi2_reversal.config import (
    SPYRsi2Config,
    create_default_config,
)
from trading.experiments.spy_004_rsi2_reversal.signal_detector import (
    SPYRsi2SignalDetector,
)


class SPYRsi2Strategy(ExecutionModelStrategy):
    """SPY RSI(2) 極端超賣均值回歸 (SPY-004)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPYRsi2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPYRsi2Config):
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

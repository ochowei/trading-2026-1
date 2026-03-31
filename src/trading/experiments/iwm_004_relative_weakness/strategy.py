"""
IWM-004: RSI(2) 極端超賣均值回歸（TP +4.0% 測試）
(IWM RSI(2) Extreme Oversold Mean Reversion - TP +4.0% Test)

使用 RSI(2) 訊號架構搭配 ExecutionModelBacktester 固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_004_relative_weakness.config import (
    IWM004Config,
    create_default_config,
)
from trading.experiments.iwm_004_relative_weakness.signal_detector import (
    IWM004SignalDetector,
)


class IWM004Strategy(ExecutionModelStrategy):
    """IWM RSI(2) TP +4.0% 測試 (IWM-004)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM004SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM004Config):
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

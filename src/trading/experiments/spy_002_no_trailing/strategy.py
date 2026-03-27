"""
SPY-002: 回檔 + Williams %R + 反轉K線（無追蹤停損版）
(SPY Pullback + WR + Reversal Candle, No Trailing Stop)

移除追蹤停損，使用標準 ExecutionModelBacktester 固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_002_no_trailing.config import (
    SPYNoTrailingConfig,
    create_default_config,
)
from trading.experiments.spy_002_no_trailing.signal_detector import (
    SPYNoTrailingSignalDetector,
)


class SPYNoTrailingStrategy(ExecutionModelStrategy):
    """SPY 回檔 + WR + 反轉K線（無追蹤停損）(SPY-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPYNoTrailingSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPYNoTrailingConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

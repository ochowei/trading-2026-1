"""
TLT 回檔範圍 + Williams %R + 反轉K線均值回歸策略
(TLT Pullback Range + Williams %R + Reversal Candle Mean Reversion Strategy)

進場使用 10 日高點回檔範圍 3-7% + Williams %R + 收盤位置三重確認，固定出場。
Entry uses pullback range 3-7% from 10-day high + Williams %R + close position.
Fixed exit, no trailing stop.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_001_pullback_wr_reversal.config import (
    TLTPullbackWRReversalConfig,
    create_default_config,
)
from trading.experiments.tlt_001_pullback_wr_reversal.signal_detector import (
    TLTPullbackWRReversalSignalDetector,
)


class TLTPullbackWRReversalStrategy(ExecutionModelStrategy):
    """TLT 回檔範圍 + Williams %R + 反轉K線均值回歸策略 (TLT-001)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLTPullbackWRReversalSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLTPullbackWRReversalConfig):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

"""
XLU-010: 20-Day Wide Pullback + Williams %R + Reversal Candle
(XLU 20日寬回檔 + Williams %R + 反轉K線)

COPX-003 insight: 20-day lookback + wider pullback range = better Part A Sharpe.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_010_20d_wide_pullback.config import (
    XLU20dWidePullbackConfig,
    create_default_config,
)
from trading.experiments.xlu_010_20d_wide_pullback.signal_detector import (
    XLU20dWidePullbackSignalDetector,
)


class XLU20dWidePullbackStrategy(ExecutionModelStrategy):
    """XLU 20日寬回檔 + Williams %R + 反轉K線 (XLU-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU20dWidePullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU20dWidePullbackConfig):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R 期數: {config.wr_period}")
            print(f"  Williams %R 門檻: <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

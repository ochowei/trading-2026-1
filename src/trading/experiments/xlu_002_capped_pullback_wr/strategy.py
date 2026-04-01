"""
XLU-002: Capped Pullback + Williams %R + Reversal Candle
(XLU 回檔範圍 + Williams %R + 反轉K線)

基於 XLU-001 框架，加入回檔上限 7% 過濾利率上升期持續下跌。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_002_capped_pullback_wr.config import (
    XLUCappedPullbackConfig,
    create_default_config,
)
from trading.experiments.xlu_002_capped_pullback_wr.signal_detector import (
    XLUCappedPullbackSignalDetector,
)


class XLURsi2ReversalStrategy(ExecutionModelStrategy):
    """XLU 回檔範圍 + Williams %R + 反轉K線 (XLU-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLUCappedPullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLUCappedPullbackConfig):
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

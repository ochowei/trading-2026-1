"""
XLU-003: Tight Pullback + Williams %R + Reversal Candle
(XLU 緊縮回檔門檻 + Williams %R + 反轉K線)

基於 XLU-002 框架，提高回檔下限從 3% → 3.5%。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_003_tight_pullback_wr.config import (
    XLUTightPullbackConfig,
    create_default_config,
)
from trading.experiments.xlu_003_tight_pullback_wr.signal_detector import (
    XLUTightPullbackSignalDetector,
)


class XLUTightPullbackStrategy(ExecutionModelStrategy):
    """XLU 緊縮回檔門檻 + Williams %R + 反轉K線 (XLU-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLUTightPullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLUTightPullbackConfig):
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

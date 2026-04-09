"""
XLU-011: Volatility-Adaptive Mean Reversion
(XLU 波動率自適應均值回歸)

XLU-003 framework + ATR ratio filter (1.15 threshold) to distinguish
sharp pullbacks from gradual declines.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_011_vol_adaptive_mr.config import (
    XLUVolAdaptiveMRConfig,
    create_default_config,
)
from trading.experiments.xlu_011_vol_adaptive_mr.signal_detector import (
    XLUVolAdaptiveMRDetector,
)


class XLUVolAdaptiveMRStrategy(ExecutionModelStrategy):
    """XLU 波動率自適應均值回歸 (XLU-011)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLUVolAdaptiveMRDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLUVolAdaptiveMRConfig):
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
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

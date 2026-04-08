"""
XLU-010: Pullback + Williams %R + 2-Day Sharp Decline
(XLU 回檔 + Williams %R + 2日急跌過濾)

基於 XLU-003，加入 2日跌幅過濾移除漸進式下跌假訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_010_pullback_wr_2d_drop.config import (
    XLUPullbackWR2dDropConfig,
    create_default_config,
)
from trading.experiments.xlu_010_pullback_wr_2d_drop.signal_detector import (
    XLUPullbackWR2dDropSignalDetector,
)


class XLUPullbackWR2dDropStrategy(ExecutionModelStrategy):
    """XLU 回檔 + Williams %R + 2日急跌過濾 (XLU-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLUPullbackWR2dDropSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLUPullbackWR2dDropConfig):
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
            print(f"  2日跌幅 (2-Day Drop): <= {config.drop_2d_threshold:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

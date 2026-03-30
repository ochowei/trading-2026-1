"""
XLU 回檔 + Williams %R + 反轉K線均值回歸策略
(XLU Pullback + Williams %R + Reversal Candle Mean Reversion Strategy)
進場使用 10 日高點回檔 + Williams %R + 收盤位置三重確認，固定 TP/SL 出場。
Entry uses pullback from 10-day high + Williams %R + close position triple confirmation.
Exit uses fixed TP/SL (no trailing stop).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_001_pullback_wr_reversal.config import (
    XLUPullbackWRReversalConfig,
    create_default_config,
)
from trading.experiments.xlu_001_pullback_wr_reversal.signal_detector import (
    XLUPullbackWRReversalSignalDetector,
)


class XLUPullbackWRReversalStrategy(ExecutionModelStrategy):
    """XLU 回檔 + Williams %R + 反轉K線均值回歸策略 (XLU-001)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLUPullbackWRReversalSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLUPullbackWRReversalConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""
TLT-005: Donchian ���破 + 趨勢跟蹤
(TLT Donchian Channel Breakout + Trend Following)

使用 Donchian Channel 突破進場搭配 SMA 趨勢確認，固定 TP/SL 出場。
Entry uses Donchian Channel breakout with SMA trend filter, fixed TP/SL exit.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_005_donchian_momentum.config import (
    TLTBreakoutTrendConfig,
    create_default_config,
)
from trading.experiments.tlt_005_donchian_momentum.signal_detector import (
    TLTBreakoutTrendSignalDetector,
)


class TLTBreakoutTrendStrategy(ExecutionModelStrategy):
    """TLT Donchian 突�� + 趨勢跟蹤 (TLT-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLTBreakoutTrendSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLTBreakoutTrendConfig):
            print(f"  Donchian 突破期數: {config.donchian_period} 日最高價")
            print(f"  趨勢確認 SMA: SMA({config.sma_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

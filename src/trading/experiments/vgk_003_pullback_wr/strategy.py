"""
VGK-003: 回檔 + Williams %R + ATR 均值回歸
(VGK Pullback + Williams %R + ATR Mean Reversion)

10 日高點回檔 + Williams %R + 收盤位置確認 + ATR 波動率飆升過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_003_pullback_wr.config import (
    VGK003Config,
    create_default_config,
)
from trading.experiments.vgk_003_pullback_wr.signal_detector import (
    VGK003SignalDetector,
)


class VGK003Strategy(ExecutionModelStrategy):
    """VGK 回檔 + Williams %R 均值回歸 (VGK-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK003Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
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

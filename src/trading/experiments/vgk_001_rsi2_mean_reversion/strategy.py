"""
VGK-001: RSI(2) 均值回歸
(VGK RSI(2) Mean Reversion)

使用 RSI(2) 訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_001_rsi2_mean_reversion.config import (
    VGKRsi2MeanReversionConfig,
    create_default_config,
)
from trading.experiments.vgk_001_rsi2_mean_reversion.signal_detector import (
    VGKRsi2MeanReversionSignalDetector,
)


class VGKRsi2MeanReversionStrategy(ExecutionModelStrategy):
    """VGK RSI(2) 均值回歸 (VGK-001)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGKRsi2MeanReversionSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGKRsi2MeanReversionConfig):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

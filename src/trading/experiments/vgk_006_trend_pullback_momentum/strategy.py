"""
VGK-006: Trend Pullback Momentum
(Failed — did not surpass VGK-003 Att2 min 0.42)

Three iterations tested, all failed:
- Att1 (SMA trend + shallow PB): min 0.02
- Att2 (SMA trend + wider exits): min -0.21
- Att3 (ROC momentum): min 0.00 (0 OOS signals)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_006_trend_pullback_momentum.config import (
    VGK006Config,
    create_default_config,
)
from trading.experiments.vgk_006_trend_pullback_momentum.signal_detector import (
    VGK006SignalDetector,
)


class VGK006Strategy(ExecutionModelStrategy):
    """VGK Trend Pullback Momentum (VGK-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK006SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK006Config):
            print(
                f"  Trend: SMA({config.sma_short_period})"
                f" > SMA({config.sma_long_period})"
                f", Close > SMA({config.sma_long_period})"
            )
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.1%}"
                f" <= {abs(config.pullback_cap):.1%}"
            )
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

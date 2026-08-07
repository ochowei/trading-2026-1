"""TQQQ-005: soft VIX filter with adaptive exits."""

from trading.core.base_backtester import BaseBacktester
from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.experiments.tqqq_003_cap_wider_exit.backtester import TrailingStopBacktester
from trading.experiments.tqqq_005_cap_vix_adaptive.config import (
    TQQQCapVixAdaptiveConfig,
    create_default_config,
)
from trading.experiments.tqqq_005_cap_vix_adaptive.signal_detector import (
    TQQQCapVixAdaptiveDetector,
)


class TQQQCapVixAdaptiveStrategy(AuxiliaryBundleStrategyMixin, BaseStrategy):
    """TQQQ soft-VIX filter and adaptive exits with a verified ^VIX bundle."""

    bundle_trial_family = "TQQQ:vix-adaptive-capitulation"
    bundle_trial_hypothesis = "TQQQ capitulation entries improve when VIX clears a soft fear threshold and exits adapt to VIX tiers."

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapVixAdaptiveDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> BaseBacktester:
        if isinstance(config, TQQQCapVixAdaptiveConfig):
            return TrailingStopBacktester(config)
        return super().create_backtester(config)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQCapVixAdaptiveConfig):
            print(f"  回撤閾值: {config.drawdown_threshold:.0%}")
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  VIX 門檻: >= {config.vix_threshold}")
            print(f"  追蹤停利: {config.trailing_stop_pct:.0%}")
        super()._print_strategy_params(config)

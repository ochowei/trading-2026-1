"""TQQQ-004: VIX-filtered capitulation strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.experiments.tqqq_004_cap_vix_filter.config import (
    TQQQCapVixFilterConfig,
    create_default_config,
)
from trading.experiments.tqqq_004_cap_vix_filter.signal_detector import (
    TQQQCapVixFilterDetector,
)


class TQQQCapVixFilterStrategy(AuxiliaryBundleStrategyMixin, BaseStrategy):
    """TQQQ capitulation signals filtered by a verified ^VIX bundle."""

    bundle_trial_family = "TQQQ:vix-filter-capitulation"
    bundle_trial_hypothesis = (
        "TQQQ capitulation entries improve when VIX confirms elevated market fear."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapVixFilterDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQCapVixFilterConfig):
            print(f"  回撤閾值: {config.drawdown_threshold:.0%}")
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  VIX 門檻: > {config.vix_threshold}")
        super()._print_strategy_params(config)

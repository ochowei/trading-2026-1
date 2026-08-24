"""TQQQ-014: VIX-adaptive exits with the execution model."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.backtester import VIXAdaptiveBacktester
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.config import (
    TQQQVixAdaptiveConfig,
    create_default_config,
)
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.signal_detector import (
    TQQQVixAdaptiveDetector,
)


class TQQQVixAdaptiveStrategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """TQQQ VIX-adaptive exits using a verified ^VIX historical bundle."""

    bundle_trial_family = "TQQQ:vix-adaptive-execution"
    bundle_trial_hypothesis = (
        "TQQQ exit tiers improve when the signal-day VIX regime is supplied without look-ahead."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQVixAdaptiveDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> VIXAdaptiveBacktester:
        slippage = config.slippage_pct if isinstance(config, TQQQVixAdaptiveConfig) else 0.001
        return VIXAdaptiveBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQVixAdaptiveConfig):
            print(f"  VIX data source: {config.vix_ticker}")
            print(f"  冷卻期: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""XLU-006: pullback/WR entry with a TLT rate-regime filter."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_006_rsi2_wide_sl.config import (
    XLU006Config,
    create_default_config,
)
from trading.experiments.xlu_006_rsi2_wide_sl.signal_detector import (
    XLURSI2WideSLSignalDetector,
)


class XLURSI2WideSLStrategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """XLU pullback/WR signals filtered by a verified TLT rate bundle."""

    bundle_trial_family = "XLU:tlt-rate-filter"
    bundle_trial_hypothesis = (
        "XLU pullback mean reversion improves when TLT avoids a rapid rate-driven drawdown regime."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLURSI2WideSLSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU006Config):
            print(
                f"  回檔範圍: {config.pullback_lookback}d "
                f"{abs(config.pullback_threshold):.1%}-{abs(config.pullback_cap):.1%}"
            )
            print(f"  TLT ROC({config.tlt_roc_period}) > {config.tlt_roc_threshold:.1%}")
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

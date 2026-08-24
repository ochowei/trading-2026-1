"""TQQQ-007: QQQ RSI confirmation strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.experiments.tqqq_007_cap_qqq_confirm.config import (
    TQQQCapQqqConfirmConfig,
    create_default_config,
)
from trading.experiments.tqqq_007_cap_qqq_confirm.signal_detector import (
    TQQQCapQqqConfirmDetector,
)


class TQQQCapQqqConfirmStrategy(AuxiliaryBundleStrategyMixin, BaseStrategy):
    """TQQQ capitulation signals confirmed by a verified QQQ bundle."""

    bundle_trial_family = "TQQQ:qqq-confirm-capitulation"
    bundle_trial_hypothesis = (
        "TQQQ capitulation entries improve when QQQ RSI confirms broad-market weakness."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapQqqConfirmDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQCapQqqConfirmConfig):
            print(f"  回撤閾值: {config.drawdown_threshold:.0%}")
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  QQQ RSI({config.qqq_rsi_period}) < {config.qqq_rsi_threshold}")
        super()._print_strategy_params(config)

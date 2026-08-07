"""TQQQ-012: QQQ confirmation with the execution model."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_012_cap_exec_qqq_confirm.config import (
    TQQQCapExecQqqConfirmConfig,
    create_default_config,
)
from trading.experiments.tqqq_012_cap_exec_qqq_confirm.signal_detector import (
    TQQQCapExecQqqConfirmDetector,
)


class TQQQCapExecQqqConfirmStrategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """TQQQ QQQ confirmation plus next-open execution from a verified bundle."""

    bundle_trial_family = "TQQQ:qqq-confirm-execution"
    bundle_trial_hypothesis = (
        "TQQQ capitulation execution improves when QQQ RSI confirms broad-market weakness."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapExecQqqConfirmDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = config.slippage_pct if isinstance(config, TQQQCapExecQqqConfirmConfig) else 0.001
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQCapExecQqqConfirmConfig):
            print(f"  回撤閾值: {config.drawdown_threshold:.0%}")
            print(f"  QQQ RSI({config.qqq_rsi_period}) < {config.qqq_rsi_threshold}")
        super()._print_strategy_params(config)

"""TQQQ-015: QQQ trend breakout signals traded through TQQQ."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_015_qqq_trend_breakout.config import (
    TQQQQqqBreakoutConfig,
    create_default_config,
)
from trading.experiments.tqqq_015_qqq_trend_breakout.signal_detector import (
    TQQQQqqBreakoutDetector,
)


class TQQQQqqTrendBreakoutStrategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """Trade TQQQ from QQQ momentum signals supplied by a verified bundle."""

    bundle_trial_family = "TQQQ:qqq-trend-breakout"
    bundle_trial_hypothesis = (
        "TQQQ breakout entries improve when QQQ momentum and long-term trend confirm the move."
    )

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQQqqBreakoutDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = config.slippage_pct if isinstance(config, TQQQQqqBreakoutConfig) else 0.001
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQQqqBreakoutConfig):
            print(f"  QQQ ROC(10) > {config.momentum_threshold}%")
            print(f"  冷卻期: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

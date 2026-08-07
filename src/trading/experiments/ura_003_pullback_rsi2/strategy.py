"""
URA-003: 回檔 + RSI(2) 策略
(URA Pullback + RSI(2) Strategy)

基於 URA-002 架構，以 RSI(2) < 15 替代 WR(10) ≤ -80。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import PrimaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_003_pullback_rsi2.config import (
    URAPullbackRSI2Config,
    create_default_config,
)
from trading.experiments.ura_003_pullback_rsi2.signal_detector import (
    URAPullbackRSI2SignalDetector,
)


class URAPullbackRSI2Strategy(PrimaryBundleStrategyMixin, ExecutionModelStrategy):
    bundle_trial_family = "URA:pullback-rsi2"
    bundle_trial_hypothesis = (
        "URA pullback entries improve when short-horizon RSI confirms capitulation."
    )
    """URA-003：回檔 + RSI(2)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URAPullbackRSI2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URAPullbackRSI2Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

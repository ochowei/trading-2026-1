"""XBI-016: macro-confirmed pullback mean-reversion strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_016_macro_confirmed_mr.config import (
    XBI016Config,
    create_default_config,
)
from trading.experiments.xbi_016_macro_confirmed_mr.signal_detector import (
    XBI016SignalDetector,
)


class XBI016Strategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """XBI macro-confirmed pullback MR with a verified macro bundle."""

    bundle_trial_family = "XBI:macro-confirmed-mr"
    bundle_trial_hypothesis = "XBI capitulation mean reversion improves when the broad-market macro proxy confirms risk-off conditions."
    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI016Config):
            print(
                f"  回檔範圍: {config.pullback_lookback}d "
                f"{abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R({config.wr_period}) <= {config.wr_threshold}")
            print(f"  反轉K線: ClosePos >= {config.close_position_threshold:.0%}")
            print(
                f"  宏觀確認閘門: {config.macro_ticker} "
                f"{config.macro_lookback}d <= {config.macro_max_return:.1%}"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

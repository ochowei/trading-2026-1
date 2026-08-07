"""DIA-019: QQQ macro-confirmation gate mean-reversion strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_019_qqq_macro_confirm_mr.config import (
    DIA019Config,
    create_default_config,
)
from trading.experiments.dia_019_qqq_macro_confirm_mr.signal_detector import (
    DIA019SignalDetector,
)


class DIA019Strategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """DIA QQQ macro-confirmation gate MR with an explicit auxiliary bundle."""

    bundle_trial_family = "DIA:qqq-macro-confirm-mr"
    bundle_trial_hypothesis = (
        "DIA capitulation mean reversion improves when QQQ confirms a broad-market correction."
    )
    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA019SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA019Config):
            print(f"  RSI({config.rsi_period}) 門檻: < {config.rsi_threshold}")
            print(f"  {config.decline_lookback} 日跌幅門檻: >= {abs(config.decline_threshold):.1%}")
            print(f"  收盤位置: >= {config.close_position_threshold:.0%}")
            print(f"  QQQ macro gate: {config.macro_lookback}d <= {config.macro_max_return:.1%}")
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""IWM-015: QQQ macro-confirmed capitulation mean-reversion strategy."""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.bundle_strategy import AuxiliaryBundleStrategyMixin
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_015_macro_confirmed_mr.config import (
    IWM015Config,
    create_default_config,
)
from trading.experiments.iwm_015_macro_confirmed_mr.signal_detector import (
    IWM015SignalDetector,
)


class IWM015Strategy(AuxiliaryBundleStrategyMixin, ExecutionModelStrategy):
    """IWM macro-confirmed capitulation MR with a verified QQQ bundle."""

    bundle_trial_family = "IWM:qqq-macro-confirm-mr"
    bundle_trial_hypothesis = (
        "IWM capitulation mean reversion improves when QQQ confirms a broad-market correction."
    )
    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM015Config):
            print(f"  RSI({config.rsi_period}) 門檻: < {config.rsi_threshold}")
            print(f"  {config.decline_lookback} 日跌幅門檻: >= {abs(config.decline_threshold):.1%}")
            print(f"  收盤位置: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 比率: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  QQQ macro gate: {config.macro_lookback}d <= {config.macro_max_return:.1%}")
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)

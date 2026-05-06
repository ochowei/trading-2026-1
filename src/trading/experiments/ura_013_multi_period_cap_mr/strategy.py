"""
URA-013: Multi-Period Capitulation-Strength Filter MR
Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_013_multi_period_cap_mr.config import (
    URA013Config,
    create_default_config,
)
from trading.experiments.ura_013_multi_period_cap_mr.signal_detector import (
    URA013SignalDetector,
)


class URA013Strategy(ExecutionModelStrategy):
    """URA Multi-Period Capitulation-Strength Filter MR (URA-013)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA013Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2-Day Decline: <= {config.two_day_decline:.0%}")
            print(
                f"  ATR Band: {config.atr_ratio_floor} <= ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" <= {config.atr_ratio_ceiling}"
            )
            print(f"  {config.multi_period_lookback}d Return Cap: >= {config.multi_period_cap:.1%}")
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

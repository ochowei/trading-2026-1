"""
URA-012: Volatility-Acceleration-Bounded MR (ATR Ratio CEILING)
Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_012_atr_band_mr.config import (
    URA012Config,
    create_default_config,
)
from trading.experiments.ura_012_atr_band_mr.signal_detector import (
    URA012SignalDetector,
)


class URA012Strategy(ExecutionModelStrategy):
    """URA ATR-Ceiling MR (URA-012)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA012Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2-Day Decline: <= {config.two_day_decline:.0%}")
            print(
                f"  ATR Ceiling: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" <= {config.atr_ratio_ceiling}"
            )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

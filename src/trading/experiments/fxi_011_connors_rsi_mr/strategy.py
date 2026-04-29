"""
FXI-011: Connor's RSI Mean Reversion
Composite oscillator (RSI(3) + Streak_RSI(2) + PercentRank(1d, 100d)) on FXI.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_011_connors_rsi_mr.config import (
    FXI011Config,
    create_default_config,
)
from trading.experiments.fxi_011_connors_rsi_mr.signal_detector import (
    FXI011SignalDetector,
)


class FXI011Strategy(ExecutionModelStrategy):
    """FXI Connor's RSI Mean Reversion (FXI-011)"""

    slippage_pct: float = 0.001  # 0.1% ETF standard

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI011Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  Connor's RSI: CRSI("
                f"{config.crsi_rsi_period},"
                f"{config.crsi_streak_period},"
                f"{config.crsi_rank_period}"
                f") <= {config.crsi_threshold}"
            )
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(
                f"  ATR Filter: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

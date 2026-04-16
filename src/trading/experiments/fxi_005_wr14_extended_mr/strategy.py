"""
FXI-005: WR(14) Extended Cooldown Mean Reversion
Uses WR(14) + extended cooldown with ExecutionModelBacktester.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_005_wr14_extended_mr.config import (
    FXI005Config,
    create_default_config,
)
from trading.experiments.fxi_005_wr14_extended_mr.signal_detector import (
    FXI005SignalDetector,
)


class FXI005Strategy(ExecutionModelStrategy):
    """FXI WR(14) Extended MR (FXI-005)"""

    slippage_pct: float = 0.001  # 0.1% ETF standard

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI005Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(
                f"  ATR Filter: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

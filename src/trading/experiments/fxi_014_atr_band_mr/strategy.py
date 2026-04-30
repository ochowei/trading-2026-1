"""
FXI-014: Volatility-Acceleration-Bounded MR (ATR Ratio BAND)
Uses ExecutionModelBacktester (next-open + 0.1% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_014_atr_band_mr.config import (
    FXI014Config,
    create_default_config,
)
from trading.experiments.fxi_014_atr_band_mr.signal_detector import (
    FXI014SignalDetector,
)


class FXI014Strategy(ExecutionModelStrategy):
    """FXI ATR-Band MR (FXI-014)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI014Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(
                f"  ATR Band: {config.atr_ratio_floor} < ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" <= {config.atr_ratio_ceiling}"
            )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

"""
FXI-009: Failed Breakdown Reversal (Turtle Soup)
Uses ExecutionModelBacktester with next-day open entry + pessimistic exits.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_009_failed_breakdown_reversal.config import (
    FXI009Config,
    create_default_config,
)
from trading.experiments.fxi_009_failed_breakdown_reversal.signal_detector import (
    FXI009SignalDetector,
)


class FXI009Strategy(ExecutionModelStrategy):
    """FXI Failed Breakdown Reversal (FXI-009)"""

    slippage_pct: float = 0.001  # 0.1% ETF standard

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI009Config):
            print(
                f"  Breakdown: Low_{{T-1}} < {config.breakdown_lookback}d min Low"
                f" and Close_T reclaims"
            )
            print(f"  Bullish bar required: {config.bullish_close_required}")
            depth = (
                f">= {abs(config.pullback_threshold):.0%}"
                if config.pullback_threshold < 0
                else "(no floor)"
            )
            print(
                f"  Pullback gate: {config.pullback_lookback}d high, depth {depth},"
                f" cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%} of day range")
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

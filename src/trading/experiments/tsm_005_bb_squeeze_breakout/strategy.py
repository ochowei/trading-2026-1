"""
TSM-005: Bollinger Band Squeeze Breakout Strategy

Uses volatility compression + breakout instead of mean reversion.
Based on NVDA-003 success, adapted for TSM volatility profile.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_005_bb_squeeze_breakout.config import (
    TSMBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.tsm_005_bb_squeeze_breakout.signal_detector import (
    TSMBBSqueezeDetector,
)


class TSMBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """TSM-005: BB Squeeze Breakout Strategy (with execution model)"""

    slippage_pct: float = 0.0010  # 0.10% for TSM ADR

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMBBSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMBBSqueezeConfig):
            print(f"  BB Parameters: BB({config.bb_period}, {config.bb_std})")
            print(
                f"  Squeeze Condition: {config.bb_squeeze_percentile_window}-day"
                f" {config.bb_squeeze_percentile:.0%} percentile,"
                f" within {config.bb_squeeze_recent_days} days"
            )
            print(f"  Trend Confirmation: Close > SMA({config.sma_trend_period})")
            print(f"  Cooldown: {config.cooldown_days} trading days")
        super()._print_strategy_params(config)

"""
SIVR-019: GVZ Implied-Vol Direction-Floor Filter MR
Uses ExecutionModelBacktester (next-open + 0.15% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_019_gvz_direction_mr.config import (
    SIVR019Config,
    create_default_config,
)
from trading.experiments.sivr_019_gvz_direction_mr.signal_detector import (
    SIVR019SignalDetector,
)


class SIVR019Strategy(ExecutionModelStrategy):
    """SIVR GVZ Direction-Floor Filter MR (SIVR-019)"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVR019SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVR019Config):
            print(
                f"  Pullback: {config.pullback_lookback}d high"
                f" >= {abs(config.pullback_threshold):.0%}"
                f", cap <= {abs(config.pullback_cap):.0%}"
            )
            print(f"  Williams %R({config.wr_period}) <= {config.wr_threshold}")
            if config.use_rsi_hook:
                print(
                    f"  RSI({config.rsi_period}) Bullish Hook: "
                    f"lookback {config.rsi_hook_lookback}d"
                    f" / delta >= {config.rsi_hook_delta}"
                    f" / near-low <= {config.rsi_hook_max_min}"
                )
            if config.use_atr_band:
                print(
                    f"  ATR Ceiling: ATR({config.atr_short_period})"
                    f"/ATR({config.atr_long_period}) <= {config.atr_ratio_ceiling}"
                )
            if config.use_3d_floor:
                print(f"  3d return floor: ret_3d <= {config.three_day_floor:.1%}")
            if config.use_gvz_direction_filter:
                print(
                    f"  ^GVZ Direction Floor: GVZ {config.gvz_direction_lookback}d"
                    f" change >= {config.min_gvz_direction_change:+.2f}"
                )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

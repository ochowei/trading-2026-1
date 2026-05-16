"""
SIVR-019: SIVR–USD Cross-Asset Divergence Regime-Gated MR
Uses ExecutionModelBacktester (next-open + 0.15% slippage + pessimistic intrabar).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_019_usd_regime_mr.config import (
    SIVR019Config,
    create_default_config,
)
from trading.experiments.sivr_019_usd_regime_mr.signal_detector import (
    SIVR019SignalDetector,
)


class SIVR019Strategy(ExecutionModelStrategy):
    """SIVR–USD Cross-Asset Divergence Regime-Gated MR (SIVR-019)"""

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
            if config.use_usd_ceiling:
                print(
                    f"  USD regime CEILING: {config.usd_ticker} "
                    f"{config.usd_lookback}d return <= {config.max_usd_return:.1%}"
                )
            if config.use_usd_divergence:
                print(
                    f"  SIVR-USD divergence FLOOR: SIVR{config.usd_lookback}d - "
                    f"{config.usd_ticker}{config.usd_lookback}d "
                    f">= {config.min_relative_return:.1%}"
                )
            print(f"  Cooldown: {config.cooldown_days} days")
        super()._print_strategy_params(config)

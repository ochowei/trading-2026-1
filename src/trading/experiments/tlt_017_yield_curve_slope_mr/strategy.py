"""TLT Yield-Curve-Slope Inflation-Regime-Gated MR 策略 (TLT-017)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_017_yield_curve_slope_mr.config import (
    TLT017Config,
    create_default_config,
)
from trading.experiments.tlt_017_yield_curve_slope_mr.signal_detector import (
    TLT017SignalDetector,
)


class TLT017YieldCurveSlopeMRStrategy(ExecutionModelStrategy):
    """TLT-017: BB-width + ^MOVE LEVEL + TLT-SPY divergence + yield curve slope
    velocity regime gate MR"""

    slippage_pct: float = 0.001  # 0.1% (TLT 高流動 ETF)

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT017SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT017Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  BB regime gate: BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            print(
                f"  MOVE implied-vol gate: {config.move_ticker} Close <="
                f" {config.max_move_level:.1f}"
            )
            print(
                f"  Cross-asset divergence gate: TLT vs {config.benchmark_ticker}"
                f" {config.divergence_lookback}d return diff >="
                f" {config.min_relative_return:+.1%}"
            )
            print(
                f"  Yield curve slope gate: ({config.long_yield_ticker} -"
                f" {config.short_yield_ticker}) {config.slope_lookback}d change"
                f" <= {config.max_slope_change:+.3f} (% points)"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

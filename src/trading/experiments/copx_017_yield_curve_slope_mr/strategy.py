"""COPX Yield-Curve-Slope Industrial-Demand-Regime-Gated MR 策略 (COPX-017)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_017_yield_curve_slope_mr.config import (
    COPX017Config,
    create_default_config,
)
from trading.experiments.copx_017_yield_curve_slope_mr.signal_detector import (
    COPX017SignalDetector,
)


class COPX017YieldCurveSlopeMRStrategy(ExecutionModelStrategy):
    """COPX-017: vol-adaptive MR + yield curve slope velocity regime gate"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPX017SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPX017Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(
                f"  Yield curve slope gate: ({config.long_yield_ticker} -"
                f" {config.short_yield_ticker}) {config.slope_lookback}d change"
                f" >= {config.min_slope_change:+.3f} (% points)"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

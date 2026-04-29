"""TLT Yield-Velocity-Gated Mean Reversion 策略 (TLT-009)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_009_yield_velocity_mr.config import (
    TLT009Config,
    create_default_config,
)
from trading.experiments.tlt_009_yield_velocity_mr.signal_detector import (
    TLT009SignalDetector,
)


class TLT009YieldVelocityMRStrategy(ExecutionModelStrategy):
    """TLT-009：^TNX yield velocity gate 均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（TLT 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT009Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  Yield Gate: {config.yield_ticker} {config.yield_lookback}d change"
                f" <= +{config.max_yield_change * 100:.0f}bps"
            )
            if config.max_bb_width_ratio is not None:
                print(
                    f"  BB 寬度 Gate (Hybrid): BB({config.bb_period}, {config.bb_std}) width"
                    f" / Close < {config.max_bb_width_ratio:.1%}"
                )
            else:
                print("  BB 寬度 Gate: 停用 (pure yield gate mode)")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

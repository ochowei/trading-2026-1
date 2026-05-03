"""USO ^OVX Implied-Vol DIRECTION Regime-Gated MR 策略 (USO-025)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_025_ovx_implied_vol_mr.config import (
    USO025Config,
    create_default_config,
)
from trading.experiments.uso_025_ovx_implied_vol_mr.signal_detector import (
    USO025SignalDetector,
)


class USO025Strategy(ExecutionModelStrategy):
    """USO-025：USO-013 框架 + ^OVX forward-looking implied vol DIRECTION gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO025SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO025Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_max):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2 日報酬 (2-Day Drop) <= {config.drop_2d_threshold:.1%}")
            if config.use_ovx_direction_filter:
                print(
                    f"  OVX direction filter: {config.ovx_ticker} "
                    f"{config.ovx_direction_lookback}d change "
                    f"<= {config.max_ovx_change:+.1f}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

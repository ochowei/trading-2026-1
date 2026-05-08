"""USO ^OVX 5d Direction Multi-Window IV Regime Gate MR 策略 (USO-028)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_028_ovx_5d_direction_mr.config import (
    USO028Config,
    create_default_config,
)
from trading.experiments.uso_028_ovx_5d_direction_mr.signal_detector import (
    USO028SignalDetector,
)


class USO028Strategy(ExecutionModelStrategy):
    """USO-028：USO-027 Att2 框架 + ^OVX 5d direction multi-window IV combo gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO028SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO028Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_max):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2 日報酬 floor (2d Drop floor) <= {config.drop_2d_threshold:.1%}")
            if config.use_ovx_3d_filter:
                print(
                    f"  ^OVX 3d direction filter: {config.ovx_ticker} "
                    f"{config.ovx_3d_lookback}d change "
                    f"<= {config.max_ovx_3d_change:+.1f}"
                )
            if config.use_return_5d_cap:
                print(
                    f"  {config.return_5d_lookback}d return cap "
                    f">= {config.return_5d_min:.1%} (multi-day persistence gate)"
                )
            if config.use_ovx_5d_filter:
                print(
                    f"  ^OVX 5d direction filter (USO-028 NEW): "
                    f"{config.ovx_5d_lookback}d change "
                    f"<= {config.max_ovx_5d_change:+.1f}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

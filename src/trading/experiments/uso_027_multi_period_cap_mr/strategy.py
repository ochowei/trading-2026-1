"""USO Multi-Period Capitulation-Strength Filter MR 策略 (USO-027)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_027_multi_period_cap_mr.config import (
    USO027Config,
    create_default_config,
)
from trading.experiments.uso_027_multi_period_cap_mr.signal_detector import (
    USO027SignalDetector,
)


class USO027Strategy(ExecutionModelStrategy):
    """USO-027：USO-025 Att3 框架 + 5d return cap multi-period persistence gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO027SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO027Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_max):.1%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2 日報酬 floor (2d Drop floor) <= {config.drop_2d_threshold:.1%}")
            if config.use_ovx_direction_filter:
                print(
                    f"  OVX direction filter: {config.ovx_ticker} "
                    f"{config.ovx_direction_lookback}d change "
                    f"<= {config.max_ovx_change:+.1f}"
                )
            if config.use_return_5d_cap:
                print(
                    f"  {config.return_5d_lookback}d return cap "
                    f">= {config.return_5d_min:.1%} (multi-day persistence gate)"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

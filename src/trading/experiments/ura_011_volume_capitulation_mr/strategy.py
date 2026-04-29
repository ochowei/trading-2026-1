"""
URA-011：成交量放大資本化均值回歸策略
(URA Volume-Confirmed Capitulation Mean Reversion Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_011_volume_capitulation_mr.config import (
    URA011Config,
    create_default_config,
)
from trading.experiments.ura_011_volume_capitulation_mr.signal_detector import (
    URA011SignalDetector,
)


class URA011Strategy(ExecutionModelStrategy):
    """URA-011：成交量放大資本化均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA011Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            if config.use_two_day_decline:
                print(f"  2日跌幅 (2-Day Decline): ≤ {config.two_day_decline:.0%}")
            print(
                f"  Volume 放大 (Volume Spike): Vol(today) / Avg{config.volume_avg_window}"
                f" ≥ {config.volume_multiple}x"
            )
            if config.use_close_pos:
                print(f"  ClosePos ≥ {config.close_pos_threshold:.0%} (日內反轉確認)")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

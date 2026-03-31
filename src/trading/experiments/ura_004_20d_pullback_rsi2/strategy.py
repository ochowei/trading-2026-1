"""
URA-004: 回檔 + RSI(2) + 2日急跌 策略
(URA Pullback + RSI(2) + 2-Day Decline Strategy)

基於 URA-003 架構，加入 2 日跌幅 ≤ -3% 作為近期恐慌確認。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_004_20d_pullback_rsi2.config import (
    URA20dPullbackRSI2Config,
    create_default_config,
)
from trading.experiments.ura_004_20d_pullback_rsi2.signal_detector import (
    URA20dPullbackRSI2SignalDetector,
)


class URA20dPullbackRSI2Strategy(ExecutionModelStrategy):
    """URA-004：回檔 + RSI(2) + 2日急跌"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA20dPullbackRSI2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA20dPullbackRSI2Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日跌幅 (2-Day Decline): ≤ {config.two_day_decline:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""
SIVR RSI(2) + 回檔範圍均值回歸策略 (SIVR RSI(2) + Capped Pullback Mean Reversion Strategy)
以 RSI(2) 替代 WR(10)，新增 2 日跌幅過濾與回檔上限。

Replaces WR(10) with RSI(2) for better match with 4-7 day holding period.
Adds 2-day decline filter and pullback cap for signal quality improvement.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_004_rsi2_pullback.config import (
    SIVRRSI2PullbackConfig,
    create_default_config,
)
from trading.experiments.sivr_004_rsi2_pullback.signal_detector import (
    SIVRRSI2PullbackSignalDetector,
)


class SIVRRSI2PullbackStrategy(ExecutionModelStrategy):
    """SIVR-004：RSI(2) + 回檔範圍均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRRSI2PullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRRSI2PullbackConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_cap):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日跌幅 (2-day decline): >= {abs(config.decline_2d_threshold):.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

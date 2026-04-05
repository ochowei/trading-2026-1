"""
DIA-007: Trend Pullback to SMA(50)
(DIA Trend Pullback Strategy)

純趨勢跟蹤策略：在上升趨勢中回測 SMA(50) 支撐時買入。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_007_trend_pullback.config import (
    DIA007TrendPullbackConfig,
    create_default_config,
)
from trading.experiments.dia_007_trend_pullback.signal_detector import (
    DIA007TrendPullbackDetector,
)


class DIATrendPullbackStrategy(ExecutionModelStrategy):
    """DIA Trend Pullback to SMA(50) (DIA-007)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA007TrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA007TrendPullbackConfig):
            print(f"  SMA 快線: {config.sma_fast_period}")
            print(f"  SMA 慢線: {config.sma_slow_period}")
            print(f"  回測接近度: {config.proximity_pct:.1%}")
            print(f"  SMA 斜率回看: {config.sma_slope_lookback} 天")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

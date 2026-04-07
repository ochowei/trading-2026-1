"""
DIA-010: RSI(5) 趨勢回調策略
(DIA RSI(5) Trend Pullback Strategy)

在上升趨勢中買入 RSI(5) 短期回調，與 DIA-001~005 均值回歸及 DIA-007 SMA proximity 不同。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_010_rsi5_trend_pullback.config import (
    DIARsi5TrendPullbackConfig,
    create_default_config,
)
from trading.experiments.dia_010_rsi5_trend_pullback.signal_detector import (
    DIARsi5TrendPullbackSignalDetector,
)


class DIARsi5TrendPullbackStrategy(ExecutionModelStrategy):
    """DIA RSI(5) 趨勢回調策略 (DIA-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIARsi5TrendPullbackSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIARsi5TrendPullbackConfig):
            print(f"  趨勢 SMA: {config.trend_sma_period} 日")
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  回調跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  策略類型: 趨勢回調 (Trend Pullback)")
        super()._print_strategy_params(config)

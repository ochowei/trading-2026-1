"""
TSM-006: Momentum Pullback 策略
TSM Momentum Pullback Strategy

在上升趨勢中買入回調，捕捉趨勢延續的動量。
與 TSM-001/002/003/004 的均值回歸和 TSM-005 的突破策略不同。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_006_momentum_pullback.config import (
    TSMMomentumPullbackConfig,
    create_default_config,
)
from trading.experiments.tsm_006_momentum_pullback.signal_detector import (
    TSMMomentumPullbackDetector,
)


class TSMMomentumPullbackStrategy(ExecutionModelStrategy):
    """TSM-006：Momentum Pullback 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMMomentumPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMMomentumPullbackConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  動量條件 (Momentum): ROC({config.roc_period}) >= {config.roc_min:.0%}")
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

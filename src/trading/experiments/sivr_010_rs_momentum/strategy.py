"""
SIVR-010: Trend Following (SMA Crossover + Pullback) 策略
SIVR Trend Following Strategy

Attempt 3: SMA 金叉 + 回調進場趨勢跟蹤策略。
在 SMA(20) > SMA(50) 的上升趨勢中，等待 3-8% 回調進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_010_rs_momentum.config import (
    SIVRRSMomentumConfig,
    create_default_config,
)
from trading.experiments.sivr_010_rs_momentum.signal_detector import (
    SIVRRSMomentumDetector,
)


class SIVRRSMomentumStrategy(ExecutionModelStrategy):
    """SIVR-010：Trend Following SMA Crossover + Pullback（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRRSMomentumDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRRSMomentumConfig):
            print(
                f"  趨勢確認 (Trend): SMA({config.sma_fast_period})"
                f" > SMA({config.sma_slow_period}) + Slope > 0"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

"""
NVDA-006: Relative Strength Momentum Pullback 策略
NVDA Relative Strength Momentum Pullback Strategy

在 NVDA 相對半導體板塊（SMH）展現超額表現時買入回調，
捕捉 NVDA 特有 alpha 而非板塊 beta。
靈感來自 TSM-007 的成功，適配 NVDA 的波動特性。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_006_relative_strength.config import (
    NVDARelativeStrengthConfig,
    create_default_config,
)
from trading.experiments.nvda_006_relative_strength.signal_detector import (
    NVDARelativeStrengthDetector,
)


class NVDARelativeStrengthStrategy(ExecutionModelStrategy):
    """NVDA-006：Relative Strength Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDARelativeStrengthDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDARelativeStrengthConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): NVDA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

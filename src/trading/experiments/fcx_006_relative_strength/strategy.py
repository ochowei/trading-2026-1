"""
FCX-006: Relative Strength 策略
FCX Relative Strength (FCX vs COPX) Strategy

買入 FCX 相對 COPX 超額表現後的短期回調，順勢捕捉個股動量。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_006_relative_strength.config import (
    FCXRelativeStrengthConfig,
    create_default_config,
)
from trading.experiments.fcx_006_relative_strength.signal_detector import (
    FCXRelativeStrengthDetector,
)


class FCXRelativeStrengthStrategy(ExecutionModelStrategy):
    """FCX-006：Relative Strength（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% FCX 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXRelativeStrengthDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXRelativeStrengthConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): FCX - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

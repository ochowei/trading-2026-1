"""
EWT-007: Relative Strength Momentum Pullback 策略
EWT Relative Strength Momentum Pullback Strategy

在 EWT 相對新興市場（EEM）展現超額表現時買入回調，
捕捉台灣半導體產業在 EM 中的結構性優勢。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_007_rs_momentum.config import (
    EWT007Config,
    create_default_config,
)
from trading.experiments.ewt_007_rs_momentum.signal_detector import (
    EWT007SignalDetector,
)


class EWT007Strategy(ExecutionModelStrategy):
    """EWT-007：Relative Strength Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT007Config):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): EWT - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

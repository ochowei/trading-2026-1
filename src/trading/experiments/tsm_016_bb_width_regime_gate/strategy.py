"""
TSM-016: BB-Width Regime Gate on RS Momentum Pullback 策略

延伸 TSM-011 Att3 RS Momentum Pullback + 5d ceiling 框架，加入
BB-Width Regime Gate（lesson #23 cross-strategy port）作為 calm regime 過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_016_bb_width_regime_gate.config import (
    TSMBBWidthRegimeGateConfig,
    create_default_config,
)
from trading.experiments.tsm_016_bb_width_regime_gate.signal_detector import (
    TSMBBWidthRegimeGateDetector,
)


class TSMBBWidthRegimeGateStrategy(ExecutionModelStrategy):
    """TSM-016：BB-Width Regime Gate on RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMBBWidthRegimeGateDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMBBWidthRegimeGateConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): TSM - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  5日報酬上限 (5d return ceiling): <= {config.ret_5d_max:+.1%}")
            print(
                f"  BB-Width Regime Gate: BB({config.bb_period},{config.bb_std})"
                f" 寬度 / Close <= {config.bb_width_max:.3f}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

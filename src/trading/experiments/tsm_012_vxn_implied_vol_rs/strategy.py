"""
TSM-012: ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback 策略

延伸 TSM-011 Att3 RS 動量回調框架，加入 ^VXN 隱含波動率 DIRECTION regime gate。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_012_vxn_implied_vol_rs.config import (
    TSMVXNImpliedVolRSConfig,
    create_default_config,
)
from trading.experiments.tsm_012_vxn_implied_vol_rs.signal_detector import (
    TSMVXNImpliedVolRSDetector,
)


class TSMVXNImpliedVolRSStrategy(ExecutionModelStrategy):
    """TSM-012：^VXN Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMVXNImpliedVolRSDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMVXNImpliedVolRSConfig):
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
                f"  隱含波動率 regime gate: {config.vxn_ticker}"
                f" {config.vxn_lookback}日變化 <= {config.vxn_change_max:+.2f}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

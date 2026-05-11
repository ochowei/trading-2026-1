"""
TSM-019: VIX Term-Structure Regime Gate on RS Momentum Pullback 策略

延伸 TSM-011 Att3 RS 動量回調 + 5d ceiling 框架，加入
^VIX3M / ^VIX 比率（VIX term structure）regime gate（lesson #24 family v9 候選）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_019_vix_term_structure_rs.config import (
    TSM019Config,
    create_default_config,
)
from trading.experiments.tsm_019_vix_term_structure_rs.signal_detector import (
    TSM019Detector,
)


class TSM019Strategy(ExecutionModelStrategy):
    """TSM-019：VIX Term-Structure Regime Gate on RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSM019Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSM019Config):
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
            if config.ret_5d_max < 1.0:
                print(f"  5日報酬上限 (5d return ceiling): <= {config.ret_5d_max:+.1%}")
            if config.max_vix_term_ratio < 999:
                print(
                    f"  VIX term structure CEILING: "
                    f"{config.vix3m_ticker}/{config.vix_ticker}"
                    f" <= {config.max_vix_term_ratio:.3f}"
                )
            if config.min_vix_term_ratio > 0.0:
                print(
                    f"  VIX term structure FLOOR: "
                    f"{config.vix3m_ticker}/{config.vix_ticker}"
                    f" >= {config.min_vix_term_ratio:.3f}"
                )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

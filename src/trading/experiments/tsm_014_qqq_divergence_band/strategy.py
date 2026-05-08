"""
TSM-014: TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback 策略

延伸 TSM-013 Att1（CEILING +15%）為雙向 BAND（FLOOR + CEILING），**repo 首次將
cross-asset divergence regime gate 從單向 CEILING/FLOOR 擴展為雙向 BAND 變體**，
直接回應 TSM-013 揭露的「Part A SLs 高 Rel_QQQ vs Part B SLs 低 Rel_QQQ」結構性
反向發現。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_014_qqq_divergence_band.config import (
    TSM014Config,
    create_default_config,
)
from trading.experiments.tsm_014_qqq_divergence_band.signal_detector import (
    TSM014QQQDivergenceBandDetector,
)


class TSM014QQQDivergenceBandStrategy(ExecutionModelStrategy):
    """TSM-014：TSM-QQQ 跨資產背離 BAND regime gate + RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSM014QQQDivergenceBandDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSM014Config):
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
            if config.ret_1d_max < 1.0:
                print(f"  1日報酬上限 (1d return ceiling): <= {config.ret_1d_max:+.1%}")
            if config.ret_5d_max < 1.0:
                print(f"  5日報酬上限 (5d return ceiling): <= {config.ret_5d_max:+.1%}")
            if config.use_divergence_filter:
                print(
                    f"  跨資產背離 BAND: TSM - {config.benchmark_ticker}"
                    f" {config.divergence_lookback}d 報酬差 ∈ "
                    f"[{config.min_relative_return:+.2%}, "
                    f"{config.max_relative_return:+.2%}]"
                )
            else:
                print("  跨資產背離: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

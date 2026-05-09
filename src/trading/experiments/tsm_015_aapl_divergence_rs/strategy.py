"""
TSM-015: TSM-AAPL Cross-Asset Divergence Regime-Gated RS Momentum Pullback 策略

延伸 TSM-013（TSM-QQQ broad benchmark anchor）為 TSM-AAPL（主要客戶 anchor），
**repo 首次將 cross-asset divergence regime gate 從 broad benchmark 擴展至主要
客戶單股 anchor**，直接回應 TSM-013 / TSM-014 揭露的 Part B SLs 在 TSM-QQQ
維度結構性無區分力的核心限制。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_015_aapl_divergence_rs.config import (
    TSM015Config,
    create_default_config,
)
from trading.experiments.tsm_015_aapl_divergence_rs.signal_detector import (
    TSM015AAPLDivergenceDetector,
)


class TSM015AAPLDivergenceStrategy(ExecutionModelStrategy):
    """TSM-015：TSM-AAPL 跨資產背離 regime gate + RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSM015AAPLDivergenceDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSM015Config):
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
            if config.use_aapl_floor or config.use_aapl_ceiling:
                lo = f"{config.min_relative_return_aapl:+.2%}" if config.use_aapl_floor else "-inf"
                hi = (
                    f"{config.max_relative_return_aapl:+.2%}" if config.use_aapl_ceiling else "+inf"
                )
                print(
                    f"  跨資產背離 BAND (主要客戶): TSM - {config.customer_ticker}"
                    f" {config.aapl_divergence_lookback}d 報酬差 ∈ [{lo}, {hi}]"
                )
            else:
                print("  跨資產背離 (AAPL): 已停用")
            if config.use_qqq_ceiling:
                print(
                    f"  跨資產背離 CEILING (大盤): TSM - {config.benchmark_ticker}"
                    f" {config.qqq_divergence_lookback}d 報酬差"
                    f" <= {config.max_relative_return_qqq:+.2%}"
                )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

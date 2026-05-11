"""
TSM-013: TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback 策略

延伸 TSM-011 Att3 RS Momentum Pullback 框架（TSM-008 base + 5d return CEILING +10.5%），
加入 TSM-QQQ 20d 報酬差 CEILING 過濾，**repo 首次將 cross-asset divergence regime
gate（CEILING 方向）移植至半導體 ADR 個股 + RS Momentum Pullback 框架**。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_013_qqq_divergence_rs.config import (
    TSM013Config,
    create_default_config,
)
from trading.experiments.tsm_013_qqq_divergence_rs.signal_detector import (
    TSM013QQQDivergenceRSDetector,
)


class TSM013QQQDivergenceRSStrategy(ExecutionModelStrategy):
    """TSM-013：TSM-QQQ 跨資產背離 CEILING regime gate + RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSM013QQQDivergenceRSDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSM013Config):
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
                    f"  跨資產背離 CEILING: TSM - {config.benchmark_ticker}"
                    f" {config.divergence_lookback}d 報酬差 ≤ "
                    f"{config.max_relative_return:+.2%}"
                )
            else:
                print("  跨資產背離: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

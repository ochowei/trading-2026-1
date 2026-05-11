"""
TSM-021: QQQ Macro-Health Gate on RS Momentum Pullback 策略

延伸 TSM-011 Att3 RS Momentum Pullback 框架，加入 QQQ broad-market macro-health
regime confirmation gate（lesson #25 cross-strategy mirror extension from IWM-015）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_021_qqq_macro_health_gate.config import (
    TSM021Config,
    create_default_config,
)
from trading.experiments.tsm_021_qqq_macro_health_gate.signal_detector import (
    TSM021QQQMacroHealthGateDetector,
)


class TSM021QQQMacroHealthGateStrategy(ExecutionModelStrategy):
    """TSM-021：QQQ Macro-Health Gate on RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSM021QQQMacroHealthGateDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSM021Config):
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
            macro_floor_active = config.macro_min_return > -1.0
            macro_ceil_active = config.macro_max_return < 1.0
            if macro_floor_active and macro_ceil_active:
                print(
                    f"  QQQ 宏觀健康閘門 (BAND): {config.macro_ticker}"
                    f" {config.macro_lookback} 日報酬"
                    f" ∈ [{config.macro_min_return:+.2%},"
                    f" {config.macro_max_return:+.2%}]"
                )
            elif macro_floor_active:
                print(
                    f"  QQQ 宏觀健康閘門 (FLOOR): {config.macro_ticker}"
                    f" {config.macro_lookback} 日報酬"
                    f" >= {config.macro_min_return:+.2%}"
                )
            elif macro_ceil_active:
                print(
                    f"  QQQ 宏觀健康閘門 (CEILING): {config.macro_ticker}"
                    f" {config.macro_lookback} 日報酬"
                    f" <= {config.macro_max_return:+.2%}"
                )
            else:
                print("  QQQ 宏觀健康閘門: 已停用")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

"""
TSM-011: Signal-Day Direction Filter on RS Momentum Pullback 策略

延伸 TSM-008 RS 動量回調框架，加入 signal-day return CEILING 過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_011_signal_day_filter.config import (
    TSMSignalDayFilterConfig,
    create_default_config,
)
from trading.experiments.tsm_011_signal_day_filter.signal_detector import (
    TSMSignalDayFilterDetector,
)


class TSMSignalDayFilterStrategy(ExecutionModelStrategy):
    """TSM-011：Signal-Day Direction Filter on RS Momentum Pullback（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMSignalDayFilterDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMSignalDayFilterConfig):
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
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

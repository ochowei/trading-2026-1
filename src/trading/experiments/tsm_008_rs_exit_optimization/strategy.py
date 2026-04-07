"""
TSM-008: RS Exit Optimization 策略
TSM Relative Strength Exit Optimization Strategy

沿用 TSM-007 進場條件，優化出場參數（TP/SL/持倉天數）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_008_rs_exit_optimization.config import (
    TSMRSExitOptConfig,
    create_default_config,
)
from trading.experiments.tsm_008_rs_exit_optimization.signal_detector import (
    TSMRSExitOptDetector,
)


class TSMRSExitOptStrategy(ExecutionModelStrategy):
    """TSM-008：RS Exit Optimization（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMRSExitOptDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMRSExitOptConfig):
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
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

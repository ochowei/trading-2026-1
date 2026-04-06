"""
NVDA-007: RS Exit Optimization 策略
NVDA RS Exit Optimization Strategy

基於 NVDA-006 的 RS 進場，優化出場參數。
借鏡 TSM-008 的延長持倉方法。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_007_rs_exit_optimized.config import (
    NVDARSExitOptimizedConfig,
    create_default_config,
)
from trading.experiments.nvda_007_rs_exit_optimized.signal_detector import (
    NVDARSExitOptimizedDetector,
)


class NVDARSExitOptimizedStrategy(ExecutionModelStrategy):
    """NVDA-007：RS Exit Optimization（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDARSExitOptimizedDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDARSExitOptimizedConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): NVDA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

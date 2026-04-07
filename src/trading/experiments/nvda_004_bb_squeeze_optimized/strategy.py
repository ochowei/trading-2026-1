"""
NVDA-004: BB Squeeze Breakout Optimized 策略
NVDA BB Squeeze Breakout Optimized Strategy

基於 NVDA-003，縮短冷卻期至 10 天以捕捉更多好訊號（Part A Sharpe +25%）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_004_bb_squeeze_optimized.config import (
    NVDABBSqueezeOptConfig,
    create_default_config,
)
from trading.experiments.nvda_004_bb_squeeze_optimized.signal_detector import (
    NVDABBSqueezeOptDetector,
)


class NVDABBSqueezeOptimizedStrategy(ExecutionModelStrategy):
    """NVDA-004：BB Squeeze Breakout Optimized 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDABBSqueezeOptDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDABBSqueezeOptConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

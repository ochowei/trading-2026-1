"""
TSLA-009: BB Wide Band Breakout 策略
TSLA BB Wide Band Breakout Strategy

以 BB(20,2.5) 寬帶突破取代 TSLA-005 的 BB(20,2.0)，
只捕捉最強勁的突破訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_009_bb_wide_breakout.config import (
    TSLABBWideConfig,
    create_default_config,
)
from trading.experiments.tsla_009_bb_wide_breakout.signal_detector import (
    TSLABBWideDetector,
)


class TSLABBWideBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-009：BB Wide Band Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLABBWideDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLABBWideConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

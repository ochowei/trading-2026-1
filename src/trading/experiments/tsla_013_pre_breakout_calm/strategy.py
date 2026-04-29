"""
TSLA-013: BB 擠壓突破 + 突破前平靜度過濾 策略
TSLA-013: BB Squeeze Breakout + Pre-Breakout Calm Filter Strategy
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_013_pre_breakout_calm.config import (
    TSLAPreBreakoutCalmConfig,
    create_default_config,
)
from trading.experiments.tsla_013_pre_breakout_calm.signal_detector import (
    TSLAPreBreakoutCalmDetector,
)


class TSLAPreBreakoutCalmStrategy(ExecutionModelStrategy):
    """TSLA-013：BB 擠壓突破 + 突破前平靜度過濾（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLAPreBreakoutCalmDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLAPreBreakoutCalmConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  突破前平靜度 (Pre-Breakout Calm): T-1 報酬 ∈ "
                f"[{config.prev_day_return_min:.1%}, {config.prev_day_return_max:.1%}]"
            )
            print(
                f"  SMA 延伸度上限 (SMA Extension Cap): "
                f"Close / SMA({config.sma_trend_period}) ≤ {config.sma_extension_max:.2f}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

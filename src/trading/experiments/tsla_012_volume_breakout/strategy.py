"""
TSLA-012: Volume-Confirmed BB Squeeze Breakout 策略
TSLA Volume-Confirmed BB Squeeze Breakout Strategy

Att2: 延長擠壓持續確認（7日內≥3日擠壓），過濾短暫波動低谷假擠壓。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_012_volume_breakout.config import (
    TSLAVolumeBreakoutConfig,
    create_default_config,
)
from trading.experiments.tsla_012_volume_breakout.signal_detector import (
    TSLAVolumeBreakoutDetector,
)


class TSLAVolumeBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-012：Volume-Confirmed BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLAVolumeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLAVolumeBreakoutConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內≥{config.bb_squeeze_min_days}日"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

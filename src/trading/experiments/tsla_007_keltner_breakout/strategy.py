"""
TSLA-007: Keltner Channel Breakout 策略
TSLA Keltner Channel Breakout Strategy

以 ATR-based Keltner Channel 取代 BB 標準差，
測試 ATR 是否對 TSLA 高波動跳空環境提供更好的擠壓/突破訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_007_keltner_breakout.config import (
    TSLAKeltnerConfig,
    create_default_config,
)
from trading.experiments.tsla_007_keltner_breakout.signal_detector import (
    TSLAKeltnerDetector,
)


class TSLAKeltnerBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-007：Keltner Channel Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLAKeltnerDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLAKeltnerConfig):
            print(
                f"  KC 參數 (Keltner Channel):"
                f" EMA({config.ema_period}), ATR({config.atr_period}) x {config.atr_multiplier}"
            )
            print(
                f"  擠壓條件 (Squeeze): {config.kc_squeeze_percentile_window}日"
                f" {config.kc_squeeze_percentile:.0%} 百分位，{config.kc_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

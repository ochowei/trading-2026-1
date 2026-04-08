"""
XLU-009: Keltner Channel Squeeze Breakout 策略
XLU KC Squeeze Breakout Strategy

以 Keltner Channel（ATR-based）取代 Bollinger Band（σ-based），
測試 ATR 波動收縮後的突破是否能產生不同且更優的訊號分布。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_009_kc_squeeze_breakout.config import (
    XLU009KCSqueezeConfig,
    create_default_config,
)
from trading.experiments.xlu_009_kc_squeeze_breakout.signal_detector import (
    XLU009KCSqueezeDetector,
)


class XLU009KCSqueezeStrategy(ExecutionModelStrategy):
    """XLU-009：KC Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU009KCSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU009KCSqueezeConfig):
            print(
                f"  KC 參數 (Keltner Channel):"
                f" EMA({config.ema_period}), ATR({config.atr_period}),"
                f" Mult {config.kc_multiplier}"
            )
            print(
                f"  擠壓條件 (Squeeze): {config.kc_squeeze_percentile_window}日"
                f" {config.kc_squeeze_percentile:.0%} 百分位，"
                f"{config.kc_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

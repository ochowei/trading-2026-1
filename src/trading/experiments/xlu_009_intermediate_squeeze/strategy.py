"""
XLU-009: Intermediate BB Squeeze Breakout 策略
XLU Intermediate BB Squeeze Breakout Strategy

BB(20,2.25) 介於 XLU-004 的 BB(20,2) 和 XLU-008 Att3 的 BB(20,2.5) 之間。
目標：在品質和訊號數量之間取得更好平衡。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_009_intermediate_squeeze.config import (
    XLU009Config,
    create_default_config,
)
from trading.experiments.xlu_009_intermediate_squeeze.signal_detector import (
    XLU009Detector,
)


class XLU009Strategy(ExecutionModelStrategy):
    """XLU-009：Intermediate BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU009Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU009Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

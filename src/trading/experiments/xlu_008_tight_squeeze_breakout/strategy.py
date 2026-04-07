"""
XLU-008: Tight BB Squeeze Breakout 策略
XLU Tight BB Squeeze Breakout Strategy

以更嚴格的波動收縮門檻和延長冷卻期優化 XLU-004，目標改善 A/B 訊號比和 Part A Sharpe。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_008_tight_squeeze_breakout.config import (
    XLU008TightSqueezeConfig,
    create_default_config,
)
from trading.experiments.xlu_008_tight_squeeze_breakout.signal_detector import (
    XLU008TightSqueezeDetector,
)


class XLU008TightSqueezeStrategy(ExecutionModelStrategy):
    """XLU-008：Tight BB Squeeze Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU008TightSqueezeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU008TightSqueezeConfig):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

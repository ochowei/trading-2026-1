"""
XLU-005: Cross-Asset Relative Value 策略
XLU Cross-Asset Relative Value Strategy

利用 XLU 與 TLT 的利率敏感性相關性，在 TLT 上漲但 XLU 滯後時買入，
預期 XLU 將補漲。一種配對交易衍生策略。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_005_trend_pullback.config import (
    XLU005Config,
    create_default_config,
)
from trading.experiments.xlu_005_trend_pullback.signal_detector import (
    XLU005Detector,
)


class XLU005TrendPullbackStrategy(ExecutionModelStrategy):
    """XLU-005：Cross-Asset Relative Value 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU005Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU005Config):
            print(
                f"  TLT 回看 (Lookback): {config.tlt_return_lookback}日，"
                f"最低漲幅 > {config.tlt_min_return:.1%}"
            )
            print(f"  XLU 滯後條件: 10日報酬 < {config.xlu_max_return:.1%}")
            print(f"  RSI({config.rsi_period}) < {config.rsi_upper:.0f}")
            print(f"  趨勢確認: Close > SMA({config.sma_long_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

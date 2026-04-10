"""
FCX-008: Trend Pullback to SMA(50) 策略
FCX Trend Pullback Strategy

趨勢跟蹤方向：在確認上升趨勢中回檔至 SMA(50) 支撐後進場。
FCX 日波動 2-4%，使用突破/趨勢風格出場（TP+8%/SL-7%/20d）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_008_trend_pullback.config import (
    FCXTrendPullbackConfig,
    create_default_config,
)
from trading.experiments.fcx_008_trend_pullback.signal_detector import (
    FCXTrendPullbackDetector,
)


class FCXTrendPullbackStrategy(ExecutionModelStrategy):
    """FCX-008：Trend Pullback 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXTrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXTrendPullbackConfig):
            print(
                f"  趨勢確認 (Trend): SMA({config.sma_fast_period})"
                f" > SMA({config.sma_slow_period}) + 上升斜率"
            )
            print(
                f"  回測門檻 (Pullback proximity): Low <= SMA(50) * {1 + config.proximity_pct:.2f}"
            )
            print(f"  斜率回看 (Slope lookback): {config.sma_slope_lookback} 交易日")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

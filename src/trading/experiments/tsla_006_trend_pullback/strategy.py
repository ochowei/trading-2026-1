"""
TSLA-006: Donchian Channel Breakout 策略
TSLA Donchian Channel Breakout Strategy

波動收縮後突破 N 日新高時進場，捕捉趨勢啟動的動能。
Att3: 改用 Donchian Channel + ATR 收縮（從 Trend Pullback 轉向）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_006_trend_pullback.config import (
    TSLATrendPullbackConfig,
    create_default_config,
)
from trading.experiments.tsla_006_trend_pullback.signal_detector import (
    TSLATrendPullbackDetector,
)


class TSLATrendPullbackStrategy(ExecutionModelStrategy):
    """TSLA-006：Donchian Channel Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLATrendPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLATrendPullbackConfig):
            print(f"  Donchian 通道 (Channel): {config.donchian_period} 日最高價")
            print(
                f"  ATR 收縮 (Contraction): ATR({config.atr_period})"
                f" ≤ {config.atr_percentile_window}日"
                f" {config.atr_percentile:.0%} 百分位，{config.atr_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

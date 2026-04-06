"""
GLD-011: Donchian Channel Breakout 策略
GLD Donchian Channel Breakout Strategy

首次在 GLD 上嘗試 Donchian 通道突破。不同於 BB Squeeze（GLD-009），
Donchian 突破捕捉價格創新高的趨勢啟動，不需要預先波動收縮。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_011_donchian_breakout.config import (
    GLD011Config,
    create_default_config,
)
from trading.experiments.gld_011_donchian_breakout.signal_detector import (
    GLD011SignalDetector,
)


class GLDDonchianBreakoutStrategy(ExecutionModelStrategy):
    """GLD-011：Donchian Channel Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD011Config):
            print(f"  Donchian 通道: {config.donchian_period} 日")
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

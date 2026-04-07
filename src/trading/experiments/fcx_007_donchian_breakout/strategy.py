"""
FCX-007: Donchian Channel Breakout 策略
FCX Donchian Channel Breakout Strategy

結合 Donchian 價格突破與 BB Squeeze 波動收縮過濾。
Donchian(30) 突破新高 + BB Squeeze 確保波動收縮後才進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_007_donchian_breakout.config import (
    FCXDonchianConfig,
    create_default_config,
)
from trading.experiments.fcx_007_donchian_breakout.signal_detector import (
    FCXDonchianDetector,
)


class FCXDonchianBreakoutStrategy(ExecutionModelStrategy):
    """FCX-007：Donchian Channel Breakout 策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXDonchianDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXDonchianConfig):
            print(f"  Donchian 通道: {config.donchian_period} 日最高價突破")
            print(f"  BB 擠壓: BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件: {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

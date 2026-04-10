"""
SIVR Donchian 通道突破策略 (SIVR-014)

突破策略：Donchian 通道突破 + SMA 趨勢確認 + 回檔要求。
與 SIVR-008 (BB Squeeze) 互補驗證不同突破定義。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_014_donchian_breakout.config import (
    SIVRDonchianBreakoutConfig,
    create_default_config,
)
from trading.experiments.sivr_014_donchian_breakout.signal_detector import (
    SIVRDonchianBreakoutSignalDetector,
)


class SIVRDonchianBreakoutStrategy(ExecutionModelStrategy):
    """SIVR-014：Donchian 通道突破"""

    slippage_pct: float = 0.0015  # 0.15%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRDonchianBreakoutSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRDonchianBreakoutConfig):
            print(f"  Donchian 通道: {config.donchian_period} 日最高 High")
            print(f"  趨勢確認: SMA({config.sma_period})")
            print(
                f"  回檔要求: 近 {config.pullback_lookback} 日內"
                f" ≥ {config.pullback_threshold:.1%} 回檔"
            )
            print(f"  SMA 斜率: SMA({config.sma_period}) 需 {config.sma_slope_lookback} 日上升")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

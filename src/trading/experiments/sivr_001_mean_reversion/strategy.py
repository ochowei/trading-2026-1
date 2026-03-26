"""
SIVR 極端超賣均值回歸策略 (SIVR Deep Oversold Mean Reversion Strategy)
雙條件進場 + 成交模型回測。
2-condition entry + execution model backtesting.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_001_mean_reversion.config import (
    SIVRMeanReversionConfig,
    create_default_config,
)
from trading.experiments.sivr_001_mean_reversion.signal_detector import (
    SIVRSignalDetector,
)


class SIVRMeanReversionStrategy(ExecutionModelStrategy):
    """SIVR-001：極端超賣均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRMeanReversionConfig):
            print(
                f"  RSI 週期/閾值 (RSI period/thr): "
                f"RSI({config.rsi_period}) < {config.rsi_threshold}"
            )
            print(
                f"  SMA 乖離閾值 (SMA dev thr): "
                f"Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.1%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

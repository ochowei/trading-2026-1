"""
NVDA 極端超賣均值回歸策略
NVDA Extreme Oversold Mean Reversion Strategy

串接配置 -> 訊號偵測器 -> 成交模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_001_extreme_oversold.config import (
    NVDAExtremeOversoldConfig,
    create_default_config,
)
from trading.experiments.nvda_001_extreme_oversold.signal_detector import (
    NVDAExtremeOversoldDetector,
)


class NVDAExtremeOversoldStrategy(ExecutionModelStrategy):
    """NVDA 極端超賣均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDAExtremeOversoldDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDAExtremeOversoldConfig):
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日急跌閾值 (2d drop): <= {config.drop_2d_threshold:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

"""
NVDA 寬獲利目標均值回歸策略
NVDA Wide TP Mean Reversion Strategy

串接配置 -> 訊號偵測器 -> 成交模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_002_capped_drawdown.config import (
    NVDACappedDrawdownConfig,
    create_default_config,
)
from trading.experiments.nvda_002_capped_drawdown.signal_detector import (
    NVDACappedDrawdownDetector,
)


class NVDACappedDrawdownStrategy(ExecutionModelStrategy):
    """NVDA 寬獲利目標均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDACappedDrawdownDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDACappedDrawdownConfig):
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日急跌閾值 (2d drop): <= {config.drop_2d_threshold:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

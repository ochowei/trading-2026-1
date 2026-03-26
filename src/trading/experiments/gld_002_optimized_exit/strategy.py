"""
GLD 優化出場均值回歸策略 (GLD Optimized Exit Mean Reversion Strategy)
進場訊號完全複用 GLD-001，僅改變出場參數。
Signal logic identical to GLD-001, only exit parameters changed.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_001_mean_reversion.signal_detector import GLDSignalDetector
from trading.experiments.gld_002_optimized_exit.config import (
    GLDOptimizedExitConfig,
    create_default_config,
)


class GLDOptimizedExitStrategy(ExecutionModelStrategy):
    """GLD 優化出場策略 (GLD-002) — 進場不變，出場優化"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLDSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLDOptimizedExitConfig):
            print(
                f"  RSI 週期/閾值 (RSI period/thr): RSI({config.rsi_period}) < {config.rsi_threshold}"
            )
            print(
                f"  SMA 乖離閾值 (SMA dev thr): Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.1%}"
            )
        super()._print_strategy_params(config)

"""
GLD 均值回歸策略
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_mean_reversion.config import GLDMeanReversionConfig, create_default_config
from trading.experiments.gld_mean_reversion.signal_detector import GLDSignalDetector

class GLDMeanReversionStrategy(ExecutionModelStrategy):
    """GLD 均值回歸策略 (Execution Model)"""
    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLDSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLDMeanReversionConfig):
            print(f"  RSI 週期/閾值 (RSI period/thr): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  SMA 乖離閾值 (SMA dev thr): Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.1%}")
        super()._print_strategy_params(config)

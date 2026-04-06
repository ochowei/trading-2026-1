"""
GLD-010: 動量回檔策略
(GLD Momentum Pullback Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_010_momentum_pullback.config import (
    GLD010Config,
    create_default_config,
)
from trading.experiments.gld_010_momentum_pullback.signal_detector import (
    GLD010SignalDetector,
)


class GLD010Strategy(ExecutionModelStrategy):
    """GLD 動量回檔 (GLD-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD010SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        return ExecutionModelBacktester(config, slippage_pct=self.slippage_pct)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD010Config):
            print(f"  動量條件 (Momentum): ROC({config.roc_period}) > {config.roc_threshold:.1%}")
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

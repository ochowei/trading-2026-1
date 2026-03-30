"""
COPX-003: 20日回檔 + Williams %R + 出場優化 均值回歸策略
(COPX 20-Day Pullback + Williams %R + Exit Optimization Strategy)

相比 COPX-002：TP +4.0%（vs +3.5%），測試更高獲利目標。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_003_exit_optimized.config import (
    COPXExitOptimizedConfig,
    create_default_config,
)
from trading.experiments.copx_003_exit_optimized.signal_detector import (
    COPXExitOptimizedSignalDetector,
)


class COPXExitOptimizedStrategy(ExecutionModelStrategy):
    """COPX-003：20日回檔 + Williams %R + 出場優化"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPXExitOptimizedSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPXExitOptimizedConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

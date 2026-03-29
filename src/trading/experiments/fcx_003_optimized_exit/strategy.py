"""
FCX 優化出場均值回歸策略
FCX Optimized Exit Mean Reversion Strategy

基於 FCX-001，調整出場參數以改善風險調整後報酬。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_003_optimized_exit.config import (
    FCXOptimizedExitConfig,
    create_default_config,
)
from trading.experiments.fcx_003_optimized_exit.signal_detector import (
    FCXOptimizedExitDetector,
)


class FCXOptimizedExitStrategy(ExecutionModelStrategy):
    """FCX 優化出場均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015  # 0.15% 個股滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXOptimizedExitDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXOptimizedExitConfig):
            print(
                f"  回撤閾值 (Drawdown thr): {config.drawdown_lookback}日高點跌幅 <= {config.drawdown_threshold:.0%}"
            )
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  SMA 乖離閾值 (SMA dev): Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.0%}"
            )
            print(f"  收盤位置閾值 (ClosePos): >= {config.close_position_threshold:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

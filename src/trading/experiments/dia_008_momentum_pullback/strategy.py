"""
DIA-008: 20-day Pullback Range + Williams %R
(DIA 20 日回檔範圍均值回歸)

跨資產驗證框架：20 日回檔範圍 + WR 超賣 + 反轉K線，
搭配 DIA 驗證過的最佳出場參數。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_008_momentum_pullback.config import (
    DIA008PullbackRangeConfig,
    create_default_config,
)
from trading.experiments.dia_008_momentum_pullback.signal_detector import (
    DIA008MomentumPullbackDetector,
)


class DIA008MomentumPullbackStrategy(ExecutionModelStrategy):
    """DIA 20-day Pullback Range + WR (DIA-008)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA008MomentumPullbackDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA008PullbackRangeConfig):
            print(f"  回檔回看: {config.pullback_lookback} 日")
            print(f"  回檔範圍: {config.pullback_min:.0%} ~ {config.pullback_max:.0%}")
            print(f"  WR 週期: {config.wr_period}")
            print(f"  WR 門檻: <= {config.wr_threshold}")
            print(f"  收盤位置: >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數: {config.cooldown_days} 天")
            print("  追蹤停損: 無 (Disabled)")
        super()._print_strategy_params(config)

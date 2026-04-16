"""
EWT-003: BB Squeeze Breakout
(EWT 布林帶擠壓突破)

完全不同於 EWT-001/002 的均值回歸方向。
利用 EWT 半導體週期驅動的波動率壓縮-突破模式。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_003_bb_squeeze_breakout.config import (
    EWT003Config,
    create_default_config,
)
from trading.experiments.ewt_003_bb_squeeze_breakout.signal_detector import (
    EWT003SignalDetector,
)


class EWT003Strategy(ExecutionModelStrategy):
    """EWT BB Squeeze Breakout (EWT-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT003Config):
            print(f"  BB 參數: BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓偵測: {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位"
                f"（近 {config.bb_squeeze_recent_days} 日內）"
            )
            print(f"  趨勢確認: SMA({config.sma_trend_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

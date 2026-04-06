"""
IWM-010: 回檔範圍 + RSI(2) 混合均值回歸
(IWM Pullback Range + RSI(2) Hybrid Mean Reversion)

使用回檔範圍結構性過濾搭配 RSI(2) 訊號架構與 ExecutionModelBacktester 固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_010_pullback_rsi2_hybrid.config import (
    IWM010Config,
    create_default_config,
)
from trading.experiments.iwm_010_pullback_rsi2_hybrid.signal_detector import (
    IWM010SignalDetector,
)


class IWM010Strategy(ExecutionModelStrategy):
    """IWM 回檔範圍 + RSI(2) 混合 (IWM-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM010Config):
            print(
                f"  回檔範圍 (Pullback Range): {config.pullback_min:.0%}-"
                f"{config.pullback_max:.0%} ({config.pullback_lookback}日回看)"
            )
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

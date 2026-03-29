"""
TSM-003: 回檔 + RSI(2) 極端超賣均值回歸
(TSM Pullback + RSI(2) Extreme Oversold Mean Reversion)

混合架構搭配 ExecutionModelBacktester 固定 TP/SL 出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_003_rsi2_reversal.config import (
    TSMRsi2Config,
    create_default_config,
)
from trading.experiments.tsm_003_rsi2_reversal.signal_detector import (
    TSMRsi2SignalDetector,
)


class TSMRsi2Strategy(ExecutionModelStrategy):
    """TSM 回檔 + RSI(2) 極端超賣均值回歸 (TSM-003)"""

    slippage_pct: float = 0.0010  # 0.10%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMRsi2SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMRsi2Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

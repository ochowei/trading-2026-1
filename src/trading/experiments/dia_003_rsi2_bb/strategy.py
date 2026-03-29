"""
DIA-003: RSI(2) 非對稱出場均值回歸
(DIA RSI(2) Asymmetric Exit Mean Reversion)

使用 DIA-002 的 RSI(2) 進場架構，搭配非對稱出場（寬 SL + 長持倉）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_003_rsi2_bb.config import (
    DIARsi2AsymConfig,
    create_default_config,
)
from trading.experiments.dia_003_rsi2_bb.signal_detector import (
    DIARsi2AsymSignalDetector,
)


class DIARsi2AsymStrategy(ExecutionModelStrategy):
    """DIA RSI(2) 非對稱出場均值回歸 (DIA-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIARsi2AsymSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIARsi2AsymConfig):
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

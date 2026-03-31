"""
DIA-005: RSI(2) 收窄停損均值回歸
(DIA RSI(2) Tighter SL Mean Reversion)

使用 DIA-004 的 RSI(2) 進場架構，測試收窄 SL -3.0%（原 -3.5%）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_005_tighter_sl.config import (
    DIARsi2TighterSLConfig,
    create_default_config,
)
from trading.experiments.dia_005_tighter_sl.signal_detector import (
    DIARsi2TighterSLSignalDetector,
)


class DIARsi2TighterSLStrategy(ExecutionModelStrategy):
    """DIA RSI(2) 收窄停損均值回歸 (DIA-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIARsi2TighterSLSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIARsi2TighterSLConfig):
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

"""
EEM-010: 嚴格跌幅 + ATR 波動率自適應 RSI(2)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_010_strict_decline_atr.config import (
    EEM010Config,
    create_default_config,
)
from trading.experiments.eem_010_strict_decline_atr.signal_detector import (
    EEM010SignalDetector,
)


class EEM010Strategy(ExecutionModelStrategy):
    """EEM 嚴格跌幅 + ATR RSI(2) 均值回歸 (EEM-010)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM010Config):
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
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

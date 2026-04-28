"""
CIBR-009: Key Reversal Day 均值回歸策略

使用 price-action 結構化的「washout + 日內反轉」進場訊號，
取代 CIBR-008 的 BB 下軌混合進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_009_key_reversal_day_mr.config import (
    CIBR009Config,
    create_default_config,
)
from trading.experiments.cibr_009_key_reversal_day_mr.signal_detector import (
    CIBR009SignalDetector,
)


class CIBR009Strategy(ExecutionModelStrategy):
    """CIBR-009：Key Reversal Day 均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR009Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日"
                f" [{abs(config.pullback_cap):.0%}, {abs(config.pullback_threshold):.0%}]"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print("  Key Reversal 結構: Prev 收黑 + Today 破前低 + Today 收盤高於前收 + Today 收紅")
            print(f"  日內反轉 (ClosePos): >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 比率: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

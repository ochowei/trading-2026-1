"""
FXI-006: Acute Decline Mean Reversion
(FXI 急跌均值回歸)

使用 2日急跌 + ATR + ClosePos 訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fxi_006_bb_lower_mr.config import (
    FXI006Config,
    create_default_config,
)
from trading.experiments.fxi_006_bb_lower_mr.signal_detector import (
    FXI006SignalDetector,
)


class FXI006Strategy(ExecutionModelStrategy):
    """FXI Acute Decline Mean Reversion (FXI-006)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FXI006SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FXI006Config):
            print(f"  2日急跌門檻: <= {config.decline_2d_threshold:.1%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

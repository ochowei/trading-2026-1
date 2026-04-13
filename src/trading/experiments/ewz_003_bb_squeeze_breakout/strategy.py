"""
EWZ-003: Acute Panic Reversal
(EWZ 急跌恐慌反轉)

使用 2日急跌 + WR + ClosePos + ATR 過濾訊號架構搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewz_003_bb_squeeze_breakout.config import (
    EWZ003Config,
    create_default_config,
)
from trading.experiments.ewz_003_bb_squeeze_breakout.signal_detector import (
    EWZ003SignalDetector,
)


class EWZ003Strategy(ExecutionModelStrategy):
    """EWZ Acute Panic Reversal (EWZ-003)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWZ003SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWZ003Config):
            print(f"  2日急跌 (2d Decline): ≤ {config.decline_2d_threshold:.1%}")
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

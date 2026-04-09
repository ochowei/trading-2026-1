"""
SIVR 急跌 + RSI(5) 均值回歸策略
(SIVR Sharp Decline + RSI(5) Mean Reversion Strategy)

改用 RSI(5) + 2 日跌幅取代 Williams %R，捕捉急速殺跌事件。
Uses RSI(5) + 2-day decline instead of Williams %R.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_011_sharp_decline_rsi5.config import (
    SIVRSharpDeclineRSI5Config,
    create_default_config,
)
from trading.experiments.sivr_011_sharp_decline_rsi5.signal_detector import (
    SIVRSharpDeclineRSI5SignalDetector,
)


class SIVRSharpDeclineRSI5Strategy(ExecutionModelStrategy):
    """SIVR-011：急跌 + RSI(5) 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRSharpDeclineRSI5SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRSharpDeclineRSI5Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  RSI: RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  急跌條件 (Decline): {config.decline_days} 日跌幅"
                f" >= {abs(config.decline_threshold):.1%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""
IWM-011: Volatility-Adaptive RSI(2) Mean Reversion
(IWM 波動率自適應 RSI(2) 均值回歸)

IWM-005 RSI(2) framework + ATR(5)/ATR(20) ratio filter to distinguish
sharp panic selling from slow drifts.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_011_vol_adaptive_rsi2.config import (
    IWM011Config,
    create_default_config,
)
from trading.experiments.iwm_011_vol_adaptive_rsi2.signal_detector import (
    IWM011SignalDetector,
)


class IWM011Strategy(ExecutionModelStrategy):
    """IWM 波動率自適應 RSI(2) 均值回歸 (IWM-011)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM011Config):
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
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

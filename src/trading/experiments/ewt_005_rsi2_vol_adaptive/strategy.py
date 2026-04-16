"""
EWT-005: RSI(2) Volatility-Adaptive Mean Reversion
(EWT RSI(2) 波動率自適應均值回歸)

完全不同的進場框架：以 RSI(2) 極端超賣取代 pullback+WR，
搭配 ATR(5)/ATR(20) 波動率飆升過濾選擇急跌恐慌進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_005_rsi2_vol_adaptive.config import (
    EWT005Config,
    create_default_config,
)
from trading.experiments.ewt_005_rsi2_vol_adaptive.signal_detector import (
    EWT005SignalDetector,
)


class EWT005Strategy(ExecutionModelStrategy):
    """EWT RSI(2) 波動率自適應均值回歸 (EWT-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWT005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWT005Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  收盤位置 (Close Position):"
                f" >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

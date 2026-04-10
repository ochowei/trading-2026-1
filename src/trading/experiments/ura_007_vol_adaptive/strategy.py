"""
URA-007: 波動率自適應均值回歸策略
(URA Volatility-Adaptive Mean Reversion Strategy)

基於 URA-004 + ATR(5)/ATR(20) 波動率飆升過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_007_vol_adaptive.config import (
    URA007Config,
    create_default_config,
)
from trading.experiments.ura_007_vol_adaptive.signal_detector import (
    URA007SignalDetector,
)


class URA007Strategy(ExecutionModelStrategy):
    """URA-007：波動率自適應均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 中等流動性 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URA007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URA007Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日跌幅 (2-Day Decline): ≤ {config.two_day_decline:.0%}")
            print(
                f"  ATR 波動率過濾: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

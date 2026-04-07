"""
XLU-007: XLU-SPY Pairs Trading 策略
XLU-SPY Pairs Trading Strategy

當 XLU 相對 SPY 顯著落後時，做多 XLU 預期防禦性輪動資金回流。
三次嘗試均未超越 XLU-004（min(A,B) 0.18），詳見 config.py 和 EXPERIMENTS_XLU.md。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_007_momentum_pullback.config import (
    XLU007Config,
    create_default_config,
)
from trading.experiments.xlu_007_momentum_pullback.signal_detector import (
    XLU007Detector,
)


class XLU007MomentumPullbackStrategy(ExecutionModelStrategy):
    """XLU-007：XLU-SPY Pairs Trading 策略（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU007Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU007Config):
            print(
                f"  配對交易 (Pairs): XLU/SPY ratio z-score({config.zscore_lookback})"
                f" < {config.zscore_threshold}"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

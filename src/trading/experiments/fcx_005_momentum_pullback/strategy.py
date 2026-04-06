"""
FCX-005: RSI(2) 短期極端超賣均值回歸策略
FCX RSI(2) Short-Term Extreme Oversold Mean Reversion Strategy

利用 RSI(2) 極端超賣捕捉 FCX 的 2 日內劇跌反彈。
與 FCX-001（60日深谷慢速抄底）和 FCX-004（BB 擠壓突破）互補。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_005_momentum_pullback.config import (
    FCXRSI2Config,
    create_default_config,
)
from trading.experiments.fcx_005_momentum_pullback.signal_detector import (
    FCXRSI2Detector,
)


class FCXMomentumPullbackStrategy(ExecutionModelStrategy):
    """FCX-005：RSI(2) 短期均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCXRSI2Detector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCXRSI2Config):
            print(f"  超賣條件 (Oversold): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  跌幅條件 (Decline): {config.decline_days}日跌幅"
                f" >= {abs(config.decline_threshold):.0%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

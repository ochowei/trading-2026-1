"""
FCX-008: 2日急跌 + 極端超賣均值回歸策略
FCX Sharp Drop + Extreme Oversold Mean Reversion Strategy

Att3: FCX-001 進場架構 + 2日急跌 <= -5% 過濾（USO-013 風格）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_008_trend_pullback.config import (
    FCX008Config,
    create_default_config,
)
from trading.experiments.fcx_008_trend_pullback.signal_detector import (
    FCX008SignalDetector,
)


class FCXTrendPullbackStrategy(ExecutionModelStrategy):
    """FCX-008：2日急跌 + 極端超賣均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX008Config):
            print(
                f"  回撤閾值 (Drawdown thr): {config.drawdown_lookback}日高點跌幅"
                f" <= {config.drawdown_threshold:.0%}"
            )
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  SMA 乖離閾值 (SMA dev): Close / SMA({config.sma_period})"
                f" - 1 <= {config.sma_deviation_threshold:.0%}"
            )
            print(f"  2日急跌 (2-day drop): <= {config.two_day_drop_threshold:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

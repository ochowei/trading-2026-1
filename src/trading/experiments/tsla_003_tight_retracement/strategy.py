"""
TSLA-003: 緊密回撤範圍均值回歸策略
TSLA Tight Retracement Mean Reversion Strategy

收窄回撤範圍 [-40%, -22%] + 2日急跌 ≥ 7%，過濾淺回調與極端崩盤。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_003_tight_retracement.config import (
    TSLATightRetracementConfig,
    create_default_config,
)
from trading.experiments.tsla_003_tight_retracement.signal_detector import (
    TSLATightRetracementDetector,
)


class TSLATightRetracementStrategy(ExecutionModelStrategy):
    """TSLA-003：緊密回撤範圍均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLATightRetracementDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLATightRetracementConfig):
            print(
                f"  回撤範圍 (Drawdown range): {config.drawdown_lookback}日高點跌幅"
                f" [{config.drawdown_upper:.0%}, {config.drawdown_threshold:.0%}]"
            )
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(f"  2日急跌 (2-day drop): <= {config.two_day_drop:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

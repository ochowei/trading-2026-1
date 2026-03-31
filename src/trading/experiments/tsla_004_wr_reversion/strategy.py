"""
TSLA-004: Williams %R 均值回歸策略
TSLA Williams %R Mean Reversion Strategy

以 WR(10) 取代 RSI(2) 作為超賣指標，其餘參數同 TSLA-002。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_004_wr_reversion.config import (
    TSLAWRReversionConfig,
    create_default_config,
)
from trading.experiments.tsla_004_wr_reversion.signal_detector import (
    TSLAWRReversionDetector,
)


class TSLAWRReversionStrategy(ExecutionModelStrategy):
    """TSLA-004：Williams %R 均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLAWRReversionDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLAWRReversionConfig):
            print(
                f"  回撤範圍 (Drawdown range): {config.drawdown_lookback}日高點跌幅"
                f" [{config.drawdown_upper:.0%}, {config.drawdown_threshold:.0%}]"
            )
            print(f"  WR 週期/閾值 (WR): WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  2日急跌 (2-day drop): <= {config.two_day_drop:.0%}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

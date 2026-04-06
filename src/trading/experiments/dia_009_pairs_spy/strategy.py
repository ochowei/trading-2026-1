"""
DIA-009: Pairs Trading (DIA/SPY) 策略
DIA/SPY Pairs Trading Strategy

利用 DIA/SPY 價格比值 z-score 均值回歸進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_009_pairs_spy.config import (
    DIAPairsSPYConfig,
    create_default_config,
)
from trading.experiments.dia_009_pairs_spy.signal_detector import (
    DIAPairsSPYDetector,
)


class DIAPairsSPYStrategy(ExecutionModelStrategy):
    """DIA-009：Pairs Trading DIA/SPY（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIAPairsSPYDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIAPairsSPYConfig):
            print(f"  配對標的 (Pair): DIA vs {config.pair_ticker}")
            print(f"  Z-Score 回看 (Lookback): {config.zscore_lookback} 日")
            print(f"  Z-Score 進場 (Entry): < {config.zscore_entry}")
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

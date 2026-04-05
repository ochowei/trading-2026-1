"""
TSM-009: Pairs Trading (TSM/NVDA) 策略
TSM/NVDA Pairs Trading Strategy

利用 TSM/NVDA 價格比值 z-score 均值回歸進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_009_pairs_trading.config import (
    TSMPairsTradingConfig,
    create_default_config,
)
from trading.experiments.tsm_009_pairs_trading.signal_detector import (
    TSMPairsTradingDetector,
)


class TSMPairsTradingStrategy(ExecutionModelStrategy):
    """TSM-009：Pairs Trading TSM/NVDA（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMPairsTradingDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMPairsTradingConfig):
            print(f"  配對標的 (Pair): TSM vs {config.pair_ticker}")
            print(f"  Z-Score 回看 (Lookback): {config.zscore_lookback} 日")
            print(f"  Z-Score 進場 (Entry): < {config.zscore_entry}")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

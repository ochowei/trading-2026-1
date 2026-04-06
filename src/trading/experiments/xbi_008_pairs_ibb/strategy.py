"""
XBI-008: Pairs Trading (XBI/IBB) 策略

利用 XBI/IBB 價格比值 z-score 均值回歸進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_008_pairs_ibb.config import (
    XBI008Config,
    create_default_config,
)
from trading.experiments.xbi_008_pairs_ibb.signal_detector import (
    XBIPairsIBBDetector,
)


class XBIPairsIBBStrategy(ExecutionModelStrategy):
    """XBI-008: Pairs Trading XBI/IBB（含成交模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBIPairsIBBDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI008Config):
            print(f"  配對標的 (Pair): XBI vs {config.pair_ticker}")
            print(f"  Z-Score 回看 (Lookback): {config.zscore_lookback} 日")
            print(f"  Z-Score 進場 (Entry): < {config.zscore_entry}")
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_period})")
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

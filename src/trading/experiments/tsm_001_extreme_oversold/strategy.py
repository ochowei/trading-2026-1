"""
TSM 極端超賣均值回歸策略
TSM Extreme Oversold Mean Reversion Strategy

串接配置 → 訊號偵測器 → 成交模型回測引擎。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_001_extreme_oversold.config import (
    TSMExtremeOversoldConfig,
    create_default_config,
)
from trading.experiments.tsm_001_extreme_oversold.signal_detector import (
    TSMExtremeOversoldDetector,
)


class TSMExtremeOversoldStrategy(ExecutionModelStrategy):
    """TSM 極端超賣均值回歸策略（含成交模型）"""

    slippage_pct: float = 0.0010  # 0.10% 大型 ADR 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMExtremeOversoldDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMExtremeOversoldConfig):
            print(
                f"  回撤閾值 (Drawdown thr): {config.drawdown_lookback}日高點跌幅 <= {config.drawdown_threshold:.0%}"
            )
            print(f"  RSI 週期/閾值 (RSI): RSI({config.rsi_period}) < {config.rsi_threshold}")
            print(
                f"  SMA 乖離閾值 (SMA dev): Close / SMA({config.sma_period}) - 1 <= {config.sma_deviation_threshold:.0%}"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

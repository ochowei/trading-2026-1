"""
NVDA-008: RS Parameter Exploration 策略
NVDA RS Parameter Exploration Strategy

探索 NVDA-006 未嘗試的 RS 參數維度：
不同回看窗口（10日/40日）和不同基準（SPY vs SMH）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.nvda_008_rs_param_explore.config import (
    NVDARSParamExploreConfig,
    create_default_config,
)
from trading.experiments.nvda_008_rs_param_explore.signal_detector import (
    NVDARSParamExploreDetector,
)


class NVDARSParamExploreStrategy(ExecutionModelStrategy):
    """NVDA-008：RS Parameter Exploration（含成交模型）"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return NVDARSParamExploreDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, NVDARSParamExploreConfig):
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  相對強度 (Relative Strength): NVDA - {config.reference_ticker}"
                f" {config.relative_strength_period}日報酬差"
                f" >= {config.relative_strength_min:.0%}"
            )
            print(
                f"  短期回調 (Pullback): {config.pullback_min:.0%}-{config.pullback_max:.0%}"
                f" from {config.pullback_lookback}日高點"
            )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)

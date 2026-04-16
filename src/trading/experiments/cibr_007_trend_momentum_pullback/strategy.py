"""
CIBR 趨勢動量回調策略 (CIBR Trend Momentum Pullback Strategy)

策略方向與前 6 個實驗不同：不是均值回歸也不是突破，
而是趨勢延續（在確認上升趨勢中買入短期回調）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_007_trend_momentum_pullback.config import (
    CIBRTrendMomentumConfig,
    create_default_config,
)
from trading.experiments.cibr_007_trend_momentum_pullback.signal_detector import (
    CIBRTrendMomentumSignalDetector,
)


class CIBRTrendMomentumStrategy(ExecutionModelStrategy):
    """CIBR-007：趨勢動量回調"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBRTrendMomentumSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBRTrendMomentumConfig):
            print(f"  趨勢確認: Close > SMA({config.sma_period})")
            print(
                f"  回調條件 (Pullback): {config.pullback_lookback} 日高點回調"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

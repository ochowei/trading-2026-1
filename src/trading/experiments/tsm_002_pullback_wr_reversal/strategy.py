"""
TSM 回檔 + Williams %R + 反轉K線均值回歸策略
TSM Pullback + Williams %R + Reversal Candle Mean Reversion Strategy

改良自 GLD-007 架構，適配 TSM 波動度，無追蹤停損。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsm_002_pullback_wr_reversal.config import (
    TSMPullbackWRReversalConfig,
    create_default_config,
)
from trading.experiments.tsm_002_pullback_wr_reversal.signal_detector import (
    TSMPullbackWRReversalDetector,
)


class TSMPullbackWRReversalStrategy(ExecutionModelStrategy):
    """TSM 回檔 + Williams %R + 反轉K線均值回歸策略 (TSM-002)"""

    slippage_pct: float = 0.0010  # 0.10% 大型 ADR 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSMPullbackWRReversalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSMPullbackWRReversalConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

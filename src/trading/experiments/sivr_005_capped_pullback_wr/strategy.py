"""
SIVR 回檔範圍 + Williams %R 均值回歸策略
(SIVR Capped Pullback + Williams %R Mean Reversion Strategy)

基於 SIVR-003，新增回檔上限過濾極端崩盤訊號。
Based on SIVR-003, adds pullback cap to filter extreme crash signals.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_005_capped_pullback_wr.config import (
    SIVRCappedPullbackWRConfig,
    create_default_config,
)
from trading.experiments.sivr_005_capped_pullback_wr.signal_detector import (
    SIVRCappedPullbackWRSignalDetector,
)


class SIVRCappedPullbackWRStrategy(ExecutionModelStrategy):
    """SIVR-005：回檔範圍 + Williams %R 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRCappedPullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRCappedPullbackWRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

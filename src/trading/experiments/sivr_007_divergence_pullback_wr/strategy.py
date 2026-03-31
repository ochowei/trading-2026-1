"""
SIVR 20日回檔範圍 + Williams %R 均值回歸策略
(SIVR 20-Day Pullback + Williams %R Mean Reversion Strategy)

基於 SIVR-005，將回檔回看窗口從 10 日擴展至 20 日。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.sivr_007_divergence_pullback_wr.config import (
    SIVRDivergencePullbackWRConfig,
    create_default_config,
)
from trading.experiments.sivr_007_divergence_pullback_wr.signal_detector import (
    SIVRDivergencePullbackWRSignalDetector,
)


class SIVRDivergencePullbackWRStrategy(ExecutionModelStrategy):
    """SIVR-007：20日回檔範圍 + Williams %R 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15%（SIVR 流動性較 GLD 低）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SIVRDivergencePullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SIVRDivergencePullbackWRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%}"
                f" ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

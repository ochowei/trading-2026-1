"""
USO 收緊出場 + 短持倉均值回歸策略 (USO-005)
基於 USO-001，使用收緊 SL (-3.25%) 及縮短持倉 (10 天)。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_005_symmetric_tight.config import (
    USOSymmetricTightConfig,
    create_default_config,
)
from trading.experiments.uso_005_symmetric_tight.signal_detector import (
    USOSymmetricTightSignalDetector,
)


class USOSymmetricTightStrategy(ExecutionModelStrategy):
    """USO-005：收緊出場 + 短持倉均值回歸"""

    slippage_pct: float = 0.001  # 0.1%

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USOSymmetricTightSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USOSymmetricTightConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

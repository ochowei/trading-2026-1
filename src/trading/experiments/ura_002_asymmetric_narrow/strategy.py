"""
URA-002: 非對稱出場 + 回檔範圍收窄策略
(URA Asymmetric Exit + Narrow Pullback Range Strategy)

基於 URA-001 架構，測試非對稱出場與回檔範圍收窄。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ura_002_asymmetric_narrow.config import (
    URAAsymmetricNarrowConfig,
    create_default_config,
)
from trading.experiments.ura_002_asymmetric_narrow.signal_detector import (
    URAAsymmetricNarrowSignalDetector,
)


class URAAsymmetricNarrowStrategy(ExecutionModelStrategy):
    """URA-002：非對稱出場 + 回檔範圍收窄"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return URAAsymmetricNarrowSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, URAAsymmetricNarrowConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

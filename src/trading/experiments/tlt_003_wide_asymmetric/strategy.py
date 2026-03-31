"""
TLT 寬停損非對稱出場均值回歸策略
(TLT Wide Asymmetric Exit Mean Reversion Strategy)

改進自 TLT-001/002：寬停損 -5.0% 給予利率波動呼吸空間，
較高獲利目標 +3.0% 補償較大虧損，冷卻期 10 天減少連續進場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_003_wide_asymmetric.config import (
    TLTWideAsymmetricConfig,
    create_default_config,
)
from trading.experiments.tlt_003_wide_asymmetric.signal_detector import (
    TLTWideAsymmetricSignalDetector,
)


class TLTWideAsymmetricStrategy(ExecutionModelStrategy):
    """TLT 寬停損非對稱出場均值回歸策略 (TLT-003)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLTWideAsymmetricSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLTWideAsymmetricConfig):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

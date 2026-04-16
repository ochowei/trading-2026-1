"""
VGK-005: 深回檔+非對稱出場+WR+ATR 均值回歸
(VGK Deep Pullback + Asymmetric Exit + WR + ATR Mean Reversion)

在 VGK-003 Att2 基礎上嘗試更深回檔門檻與非對稱出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_005_decline_enhanced_mr.config import (
    VGK005Config,
    create_default_config,
)
from trading.experiments.vgk_005_decline_enhanced_mr.signal_detector import (
    VGK005SignalDetector,
)


class VGK005Strategy(ExecutionModelStrategy):
    """VGK 深回檔+非對稱出場+WR+ATR 均值回歸 (VGK-005)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK005Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

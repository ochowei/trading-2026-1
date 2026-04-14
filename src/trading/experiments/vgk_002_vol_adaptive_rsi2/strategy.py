"""
VGK-002: RSI(2) 寬出場延長持倉均值回歸
(VGK RSI(2) Wide-Exit Extended-Hold Mean Reversion)

VGK-001 框架 + 寬出場 TP3.5%/SL-3.5% + 25 天持倉 + 10 天冷卻期。
Att1/Att2 發現 ATR 過濾在 VGK 上無效，Att3 改用延長持倉+寬出場。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.vgk_002_vol_adaptive_rsi2.config import (
    VGK002Config,
    create_default_config,
)
from trading.experiments.vgk_002_vol_adaptive_rsi2.signal_detector import (
    VGK002SignalDetector,
)


class VGK002Strategy(ExecutionModelStrategy):
    """VGK RSI(2) 寬出場延長持倉 (VGK-002)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VGK002SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VGK002Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

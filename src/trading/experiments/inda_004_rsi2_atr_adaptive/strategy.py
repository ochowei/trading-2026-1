"""
INDA-004: Short-term Momentum Crash Mean Reversion
(INDA 短期動量崩潰均值回歸)

Novel entry: WR(10) + 2-day decline + ClosePos + ATR filter.
Replaces pullback-from-high with 2-day momentum crash detection.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_004_rsi2_atr_adaptive.config import (
    INDAMomentumCrashConfig,
    create_default_config,
)
from trading.experiments.inda_004_rsi2_atr_adaptive.signal_detector import (
    INDAMomentumCrashDetector,
)


class INDAMomentumCrashStrategy(ExecutionModelStrategy):
    """INDA 短期動量崩潰均值回歸 (INDA-004)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDAMomentumCrashDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDAMomentumCrashConfig):
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  2日跌幅門檻: <= {config.decline_threshold:.1%} ({config.decline_lookback}日)")
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

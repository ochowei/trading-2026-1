"""DIA Strict-Bull-Regime Trend Pullback Continuation 策略 (DIA-013)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_013_trend_regime_pullback.config import (
    DIA013Config,
    create_default_config,
)
from trading.experiments.dia_013_trend_regime_pullback.signal_detector import (
    DIA013SignalDetector,
)


class DIA013Strategy(ExecutionModelStrategy):
    """DIA-013：嚴格 secular 多頭 regime + 趨勢回檔 continuation（執行模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA013Config):
            print(
                f"  Secular 多頭 regime: Close > SMA({config.sma_slow_period})"
                f" 且 SMA({config.sma_fast_period}) > SMA({config.sma_slow_period})"
                f" 且 SMA({config.sma_slow_period}) {config.sma_slow_slope_lookback}"
                f" 日斜率向上"
            )
            print(
                f"  上升中溫和回檔: {config.pullback_lookback} 日高點回檔"
                f" {config.pullback_min:.1%} ~ {config.pullback_max:.1%}"
            )
            print(f"  回檔轉折確認 (Close up): {config.require_close_up}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

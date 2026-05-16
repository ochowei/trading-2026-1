"""USO Trend-Following Pullback Continuation 策略 (USO-029)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_029_trend_pullback_continuation.config import (
    USO029Config,
    create_default_config,
)
from trading.experiments.uso_029_trend_pullback_continuation.signal_detector import (
    USO029SignalDetector,
)


class USO029Strategy(ExecutionModelStrategy):
    """USO-029：趨勢跟蹤回檔延續（執行模型）"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USO029SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USO029Config):
            print(
                f"  趨勢 regime: SMA({config.sma_fast}) > SMA({config.sma_slow})"
                f" 且 Close > SMA({config.sma_slow})"
            )
            print(f"  長期動量: ROC({config.roc_lookback}) > {config.roc_min:.1%}")
            print(
                f"  溫和回檔 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {config.pullback_min:.1%} ~ {config.pullback_max:.1%}"
            )
            print(f"  回檔轉折確認 (Close up): {config.require_close_up}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

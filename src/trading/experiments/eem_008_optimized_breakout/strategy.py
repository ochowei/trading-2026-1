"""
EEM-008: Optimized Breakout
(EEM 優化突破策略)

在 EEM-005 BB Squeeze 基礎上加入環境波動率過濾，
移除高波動 EM 危機期的假突破訊號。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_008_optimized_breakout.config import (
    EEM008Config,
    create_default_config,
)
from trading.experiments.eem_008_optimized_breakout.signal_detector import (
    EEM008SignalDetector,
)


class EEM008Strategy(ExecutionModelStrategy):
    """EEM 優化突破 (EEM-008)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM008Config):
            print(f"  布林帶 (BB): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓偵測: {config.bb_squeeze_percentile_window} 日"
                f" {config.bb_squeeze_percentile:.0%} 百分位,"
                f" 近 {config.bb_squeeze_recent_days} 日"
            )
            print(
                f"  環境波動率過濾: {config.realized_vol_period} 日"
                f" 實現波動率 ≤ {config.realized_vol_threshold:.1%}"
            )
            print(f"  趨勢確認: SMA({config.sma_trend_period})")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

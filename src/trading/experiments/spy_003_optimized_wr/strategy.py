"""
SPY-003: 回檔 + Williams %R + VIX 恐慌過濾
(SPY Pullback + WR + VIX Fear Filter)

使用 ExecutionModelBacktester 固定 TP/SL 出場，無追蹤停損。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_003_optimized_wr.config import (
    SPYVixFilterConfig,
    create_default_config,
)
from trading.experiments.spy_003_optimized_wr.signal_detector import (
    SPYVixFilterSignalDetector,
)


class SPYVixFilterStrategy(ExecutionModelStrategy):
    """SPY 回檔 + WR + VIX 恐慌過濾（SPY-003）"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPYVixFilterSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPYVixFilterConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(f"  VIX 恐慌門檻 (VIX threshold): >= {config.vix_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

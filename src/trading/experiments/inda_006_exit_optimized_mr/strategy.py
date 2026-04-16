"""
INDA-006: Exit-Optimized Mean Reversion
(INDA 出場優化均值回歸)

INDA-005 framework with optimized exit parameters.
Uses execution model with fixed TP/SL exit.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_006_exit_optimized_mr.config import (
    INDA006Config,
    create_default_config,
)
from trading.experiments.inda_006_exit_optimized_mr.signal_detector import (
    INDA006SignalDetector,
)


class INDA006Strategy(ExecutionModelStrategy):
    """INDA 出場優化均值回歸 (INDA-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA006SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA006Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            if config.close_position_threshold > 0:
                print(
                    f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                    " of day range"
                )
            else:
                print("  收盤位置 (Close Position): 停用 (Disabled)")
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2日急跌過濾: <= {config.drop_2d_threshold:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

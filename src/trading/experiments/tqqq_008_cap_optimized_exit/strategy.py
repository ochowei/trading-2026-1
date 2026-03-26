"""
TQQQ 優化出場策略 (TQQQ Optimized Exit Strategy)
保持基線三條件進場，優化出場參數以捕捉更大的恐慌反彈利潤。
Keeps baseline 3-condition entry; optimizes exit to capture larger panic-bounce profits.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_008_cap_optimized_exit.config import (
    TQQQCapOptimizedExitConfig,
    create_default_config,
)


class TQQQCapOptimizedExitStrategy(BaseStrategy):
    """
    TQQQ 優化出場策略 (TQQQ Optimized Exit Strategy)

    假設：基線進場最優，但 +5% 獲利目標過於保守。提高至 +7% 並延長持倉至 10 天，
    不使用追蹤停利，可捕捉更大的反彈利潤。
    Hypothesis: Baseline entry is optimal but +5% target is conservative.
    Raising to +7% with 10-day hold and no trailing stop captures larger bounces.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapOptimizedExitConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")

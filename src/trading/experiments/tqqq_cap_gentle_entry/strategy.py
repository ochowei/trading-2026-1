"""
TQQQ 溫和放寬進場策略 (TQQQ Gentle Entry Relaxation Strategy)
僅放寬 drawdown 門檻（-15% → -13%），搭配 TQQQ-008 的優化出場。
Hypothesis: TQQQ-002 failed by relaxing all 3 entry conditions simultaneously.
Relaxing only drawdown (-15% -> -13%) while keeping RSI<25 and Vol>1.5x strict
should capture additional signals without introducing noise.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_cap_gentle_entry.config import (
    TQQQCapGentleEntryConfig,
    create_default_config,
)
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector


class TQQQCapGentleEntryStrategy(BaseStrategy):
    """
    TQQQ 溫和放寬進場策略 (TQQQ Gentle Entry Relaxation Strategy)

    與 TQQQ-002 (全部放寬) 的差異：
    - TQQQ-002: DD -12%, RSI<30, Vol 1.3x → 引入過多噪音
    - TQQQ-009: DD -13%, RSI<25, Vol 1.5x → 僅溫和放寬一個條件
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapGentleEntryConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")

"""
TQQQ 放寬進場策略 (TQQQ Relaxed Entry Strategy)
放寬進場門檻（回撤 -12%、RSI < 30、量 > 1.3x）並收緊停損至 -6%。
Relaxes entry thresholds (drawdown -12%, RSI < 30, volume > 1.3x) and tightens stop-loss to -6%.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_002_cap_relaxed_entry.config import (
    TQQQCapRelaxedConfig,
    create_default_config,
)


class TQQQCapRelaxedStrategy(BaseStrategy):
    """
    TQQQ 放寬進場策略 (TQQQ Relaxed Entry Strategy)

    假設：放寬進場條件可捕捉更多機會，搭配更緊停損控制風險。
    Hypothesis: Relaxed entry captures more opportunities; tighter stop-loss manages risk.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapRelaxedConfig):
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

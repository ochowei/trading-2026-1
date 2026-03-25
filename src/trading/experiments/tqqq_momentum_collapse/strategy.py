"""
TQQQ 多日動能崩潰策略 (TQQQ Multi-Day Momentum Collapse Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_momentum_collapse.config import (
    TQQQMomentumCollapseConfig,
    create_default_config,
)
from trading.experiments.tqqq_momentum_collapse.signal_detector import (
    TQQQMomentumCollapseDetector,
)


class TQQQMomentumCollapseStrategy(BaseStrategy):
    """
    TQQQ 多日動能崩潰策略
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQMomentumCollapseDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        """印出專屬策略參數"""
        if not isinstance(config, TQQQMomentumCollapseConfig):
            super()._print_strategy_params(config)
            return

        print(f"  動能觀察天數 (Lookback window):  {config.momentum_lookback} 天")
        print(f"  下跌天數門檻 (Down days thr):    >= {config.negative_days_threshold} 天")
        print(f"  累計跌幅門檻 (Return thr):       <= {config.return_threshold:.0%}")
        print(f"  均線過濾 (SMA filter):           Close < SMA({config.sma_period})")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown days):          {config.cooldown_days} 天")

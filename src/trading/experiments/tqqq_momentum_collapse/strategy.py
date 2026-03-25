"""
TQQQ 多日動能崩潰策略 (TQQQ Multi-Day Momentum Collapse Strategy)
串接配置 → 訊號偵測器 → 通用回測引擎。
Wires config → signal detector → base backtester.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_momentum_collapse.config import (
    TQQQMomentumCollapseConfig,
    create_default_config,
)
from trading.experiments.tqqq_momentum_collapse.signal_detector import TQQQMomentumCollapseDetector


class TQQQMomentumCollapseStrategy(BaseStrategy):
    """TQQQ 多日動能崩潰策略"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQMomentumCollapseDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQMomentumCollapseConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回看區間 (Lookback):             {config.lookback_days} 天")
        print(f"  下跌日門檻 (Min down days):      >= {config.min_down_days} / {config.lookback_days}")
        print(f"  累計跌幅門檻 (5d return):        <= {config.cumulative_drop_threshold:.0%}")
        print(f"  趨勢條件 (Trend filter):         Close < SMA({config.trend_sma_period})")
        print(f"  冷卻天數 (Cooldown):             {config.cooldown_days} 天")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

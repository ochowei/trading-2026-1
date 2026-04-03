"""
IWM-007: 趨勢回檔恢復策略 (Trend Pullback Recovery)

使用 SMA(50) 回檔支撐 + 日內反彈確認，搭配 ExecutionModelBacktester。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_007_trend_pullback.config import (
    IWM007Config,
    create_default_config,
)
from trading.experiments.iwm_007_trend_pullback.signal_detector import (
    IWM007SignalDetector,
)


class IWM007Strategy(ExecutionModelStrategy):
    """IWM Trend Pullback Recovery (IWM-007)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM007SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM007Config):
            print(f"  中期均線 (SMA Mid): {config.sma_period}")
            print(f"  長期均線 (SMA Long): {config.sma_long_period}")
            print(f"  接近距離 (Proximity): {config.proximity_pct:.1%}")
            print(f"  回檔回看 (High Lookback): {config.recent_high_lookback} 日")
            print(f"  最小回檔 (Min Pullback): {config.min_pullback_pct:.1%}")
            print(f"  收盤位置 (ClosePos): >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

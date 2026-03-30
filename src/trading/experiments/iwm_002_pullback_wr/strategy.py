"""
IWM-002: 回檔 + Williams %R 均值回歸策略
(IWM Pullback + Williams %R Mean Reversion Strategy)

進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（日波動 ~1.5-2%，邊界區域預設不用）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_002_pullback_wr.config import (
    IWMPullbackWRConfig,
    create_default_config,
)
from trading.experiments.iwm_002_pullback_wr.signal_detector import (
    IWMPullbackWRSignalDetector,
)


class IWMPullbackWRStrategy(ExecutionModelStrategy):
    """IWM-002：回檔 + Williams %R 均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWMPullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWMPullbackWRConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

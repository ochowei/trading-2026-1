"""
XBI-004: 回檔範圍收窄 + 長冷卻 均值回歸策略
(XBI Capped Pullback + Extended Cooldown Mean Reversion Strategy)

進場使用 10 日高點回檔（上限 15%）+ Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（日波動 ~2%，邊界區域預設不用）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_004_capped_cooldown.config import (
    XBICappedCooldownConfig,
    create_default_config,
)
from trading.experiments.xbi_004_capped_cooldown.signal_detector import (
    XBICappedCooldownSignalDetector,
)


class XBICappedCooldownStrategy(ExecutionModelStrategy):
    """XBI-004：回檔範圍收窄 + 長冷卻 均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBICappedCooldownSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBICappedCooldownConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

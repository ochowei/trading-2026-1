"""
USO 回檔 + Williams %R 均值回歸策略 (USO Pullback + Williams %R Mean Reversion Strategy)
進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（日波動率 > 1.5%，追蹤停損已證實無效）。

Entry uses pullback from 10-day high + Williams %R confirmation.
Exit uses fixed TP/SL (no trailing stop - proven ineffective for high-vol assets).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.uso_001_pullback_wr.config import (
    USOPullbackWRConfig,
    create_default_config,
)
from trading.experiments.uso_001_pullback_wr.signal_detector import (
    USOPullbackWRSignalDetector,
)


class USOPullbackWRStrategy(ExecutionModelStrategy):
    """USO-001：回檔 + Williams %R 均值回歸"""

    slippage_pct: float = 0.001  # 0.1%（USO 流動性高，日均量 ~30M）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return USOPullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, USOPullbackWRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

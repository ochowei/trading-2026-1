"""
COPX-001: 回檔 + Williams %R 均值回歸策略
(COPX Pullback + Williams %R Mean Reversion Strategy)

進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（日波動 ~2.25%，禁用區域）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.copx_001_pullback_wr.config import (
    COPXPullbackWRConfig,
    create_default_config,
)
from trading.experiments.copx_001_pullback_wr.signal_detector import (
    COPXPullbackWRSignalDetector,
)


class COPXPullbackWRStrategy(ExecutionModelStrategy):
    """COPX-001：回檔 + Williams %R 均值回歸"""

    slippage_pct: float = 0.0015  # 0.15% 商品 ETF 滑價

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return COPXPullbackWRSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, COPXPullbackWRConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

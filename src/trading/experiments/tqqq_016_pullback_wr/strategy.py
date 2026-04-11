"""
TQQQ-016: 回檔 + Williams %R 均值回歸策略
(TQQQ Pullback + Williams %R Mean Reversion Strategy)

進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用固定止盈/停損。
不使用追蹤停損（3x 槓桿 ETF 日波動 ~5%，禁用區域）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_016_pullback_wr.config import (
    TQQQPullbackWRConfig,
    create_default_config,
)
from trading.experiments.tqqq_016_pullback_wr.signal_detector import (
    TQQQPullbackWRSignalDetector,
)


class TQQQPullbackWRStrategy(ExecutionModelStrategy):
    """TQQQ-016：回檔 + Williams %R 均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQPullbackWRSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001  # 0.1%
        if isinstance(config, TQQQPullbackWRConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TQQQPullbackWRConfig):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  成交量倍數 (Volume multiplier): {config.volume_multiplier}x")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

"""
GLD 回檔 + Williams %R 均值回歸策略 (GLD Pullback + Williams %R Mean Reversion Strategy)
進場使用 10 日高點回檔 + Williams %R 雙重確認，出場使用追蹤停損。
Entry uses pullback from 10-day high + Williams %R confirmation.
Exit uses trailing stop mechanism.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)
from trading.experiments.gld_006_pullback_wr.config import (
    GLDPullbackWRConfig,
    create_default_config,
)
from trading.experiments.gld_006_pullback_wr.signal_detector import (
    GLDPullbackWRSignalDetector,
)


class GLDPullbackWRStrategy(ExecutionModelStrategy):
    """GLD 回檔 + Williams %R 均值回歸策略 (GLD-006)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLDPullbackWRSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> TrailingStopBacktester:
        cfg = create_default_config()
        return TrailingStopBacktester(
            config,
            slippage_pct=self.slippage_pct,
            trail_activation_pct=cfg.trail_activation_pct,
            trail_distance_pct=cfg.trail_distance_pct,
        )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLDPullbackWRConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print(f"  追蹤啟動 (Trail activation): +{config.trail_activation_pct:.1%}")
            print(f"  追蹤距離 (Trail distance): {config.trail_distance_pct:.1%}")
        super()._print_strategy_params(config)

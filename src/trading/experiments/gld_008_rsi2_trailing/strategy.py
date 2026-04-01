"""
GLD-008: 20日回檔 + WR + 反轉K線 + 追蹤停損均值回歸策略
(GLD 20-Day Pullback + WR + Reversal + Trailing Stop Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)
from trading.experiments.gld_008_rsi2_trailing.config import (
    GLD008Config,
    create_default_config,
)
from trading.experiments.gld_008_rsi2_trailing.signal_detector import (
    GLD008SignalDetector,
)


class GLD008Strategy(ExecutionModelStrategy):
    """GLD 20日回檔 + WR + 反轉K線 + 追蹤停損 (GLD-008)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD008SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> TrailingStopBacktester:
        cfg = create_default_config()
        return TrailingStopBacktester(
            config,
            slippage_pct=self.slippage_pct,
            trail_activation_pct=cfg.trail_activation_pct,
            trail_distance_pct=cfg.trail_distance_pct,
        )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD008Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print(f"  追蹤啟動 (Trail activation): +{config.trail_activation_pct:.1%}")
            print(f"  追蹤距離 (Trail distance): {config.trail_distance_pct:.1%}")
        super()._print_strategy_params(config)

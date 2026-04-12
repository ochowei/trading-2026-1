"""
EWT 回檔 + Williams %R + 反轉K線均值回歸策略
(EWT Pullback + Williams %R + Reversal Candle Mean Reversion Strategy)
進場使用 10 日高點回檔 + Williams %R + 收盤位置三重確認，出場使用追蹤停損。
Entry uses pullback from 10-day high + Williams %R + close position triple confirmation.
Exit uses trailing stop mechanism.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.ewt_001_pullback_wr_reversal.config import (
    EWTPullbackWRReversalConfig,
    create_default_config,
)
from trading.experiments.ewt_001_pullback_wr_reversal.signal_detector import (
    EWTPullbackWRReversalSignalDetector,
)
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)


class EWTPullbackWRReversalStrategy(ExecutionModelStrategy):
    """EWT 回檔 + Williams %R + 反轉K線均值回歸策略 (EWT-001)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EWTPullbackWRReversalSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> TrailingStopBacktester:
        cfg = create_default_config()
        return TrailingStopBacktester(
            config,
            slippage_pct=self.slippage_pct,
            trail_activation_pct=cfg.trail_activation_pct,
            trail_distance_pct=cfg.trail_distance_pct,
        )

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EWTPullbackWRReversalConfig):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" >= {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print(f"  追蹤啟動 (Trail activation): +{config.trail_activation_pct:.1%}")
            print(f"  追蹤距離 (Trail distance): {config.trail_distance_pct:.1%}")
        super()._print_strategy_params(config)

"""GLD DXY Cross-Asset Divergence Filter on GVZ-Gated MR Strategy (GLD-016)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_016_dxy_divergence_mr.config import (
    GLD016Config,
    create_default_config,
)
from trading.experiments.gld_016_dxy_divergence_mr.signal_detector import (
    GLD016SignalDetector,
)


class GLD016DxyDivergenceMRStrategy(ExecutionModelStrategy):
    """GLD-016：GLD-015 Att2 framework + DXY cross-asset divergence regime gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD016Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(f"  2 日跌幅下限 (2d Floor): <= {config.twoday_return_floor:.1%}")
            print(f"  1 日跌幅下限 (1d Floor): <= {config.oneday_return_floor:.1%}")
            print(
                f"  GVZ DIRECTION gate: {config.gvz_ticker} "
                f"{config.gvz_direction_lookback}d change <= {config.max_gvz_direction_change:+.2f}"
            )
            print(
                f"  DXY DIRECTION gate: {config.dxy_ticker} "
                f"{config.dxy_lookback}d change <= {config.max_dxy_change:+.2%}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

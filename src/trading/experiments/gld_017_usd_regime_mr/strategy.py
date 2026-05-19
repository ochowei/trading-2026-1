"""GLD–USD Cross-Asset Divergence Regime-Gated MR 策略 (GLD-017)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_017_usd_regime_mr.config import (
    GLD017Config,
    create_default_config,
)
from trading.experiments.gld_017_usd_regime_mr.signal_detector import (
    GLD017SignalDetector,
)


class GLD017UsdRegimeMRStrategy(ExecutionModelStrategy):
    """GLD-017：GLD-015 Att2 + GLD–USD 跨資產 divergence regime gate"""

    slippage_pct: float = 0.001  # 0.1%（GLD 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD017SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD017Config):
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
            if config.use_gvz_direction_filter:
                print(
                    f"  GVZ DIRECTION gate: {config.gvz_ticker} "
                    f"{config.gvz_direction_lookback}d change <= "
                    f"{config.max_gvz_direction_change:+.2f}"
                )
            if config.use_usd_ceiling:
                print(
                    f"  USD CEILING gate: {config.usd_ticker} "
                    f"{config.usd_lookback}d return <= {config.max_usd_return:+.1%}"
                )
            if config.use_usd_divergence:
                print(
                    f"  USD DIVERGENCE gate: GLD−{config.usd_ticker} "
                    f"{config.usd_lookback}d return >= {config.min_relative_return:+.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

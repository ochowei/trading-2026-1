"""GLD GVZ Implied-Vol Forward-Looking Regime-Gated MR 策略 (GLD-015)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_015_gvz_implied_vol_mr.config import (
    GLD015Config,
    create_default_config,
)
from trading.experiments.gld_015_gvz_implied_vol_mr.signal_detector import (
    GLD015SignalDetector,
)


class GLD015GvzImpliedVolMRStrategy(ExecutionModelStrategy):
    """GLD-015：GLD-014 Att2 + ^GVZ forward-looking implied vol regime gate"""

    slippage_pct: float = 0.001  # 0.1%（GLD 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD015SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD015Config):
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
            if config.use_gvz_level_filter and config.max_gvz_level < 999.0:
                print(f"  GVZ LEVEL gate: {config.gvz_ticker} Close <= {config.max_gvz_level:.1f}")
            else:
                print("  GVZ LEVEL gate: 停用 (Disabled)")
            if config.use_gvz_direction_filter:
                print(
                    f"  GVZ DIRECTION gate: {config.gvz_ticker} "
                    f"{config.gvz_direction_lookback}d change <= {config.max_gvz_direction_change:+.2f}"
                )
            else:
                print("  GVZ DIRECTION gate: 停用 (Disabled)")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

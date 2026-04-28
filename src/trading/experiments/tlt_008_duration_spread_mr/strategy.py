"""TLT Duration-Spread Mean Reversion 策略 (TLT-008)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_008_duration_spread_mr.config import (
    TLT008Config,
    create_default_config,
)
from trading.experiments.tlt_008_duration_spread_mr.signal_detector import (
    TLT008SignalDetector,
)


class TLT008DurationSpreadMRStrategy(ExecutionModelStrategy):
    """TLT-008：TLT 相對 IEF 存續期間價差均值回歸"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT008SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT008Config):
            if config.require_mr_framework:
                print(
                    f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                    f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
                )
                print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  波動率閘門 (Vol Regime Gate): BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            op = ">=" if config.relative_direction_bullish else "<="
            if config.use_spread_zscore:
                print(
                    f"  配對過濾 (Pair filter): TLT/{config.reference_ticker} "
                    f"{config.spread_zscore_window}d z-score {op} {config.spread_zscore_threshold:.2f}"
                )
            else:
                print(
                    f"  配對過濾 (Pair filter): TLT-{config.reference_ticker} "
                    f"{config.relative_lookback}d return spread {op} {config.relative_underperf_threshold:.2%}"
                )
            if not config.require_mr_framework:
                print("  (Att1 純 pair 模式；不檢查 pullback/WR)")
                print(f"  當日轉正 (Daily up): {'是 Yes' if config.require_daily_up else '否 No'}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

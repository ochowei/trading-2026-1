"""XLU ^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR 策略 (XLU-014)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_014_tnx_rate_direction_mr.config import (
    XLU014Config,
    create_default_config,
)
from trading.experiments.xlu_014_tnx_rate_direction_mr.signal_detector import (
    XLU014SignalDetector,
)


class XLU014Strategy(ExecutionModelStrategy):
    """XLU-014：XLU-013 Att2/Att3 框架 + ^TNX realized-rate-momentum DIRECTION gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU014Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.1%} ~ {abs(config.pullback_cap):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            if config.use_move_direction_filter:
                print(
                    f"  MOVE direction filter: {config.move_ticker} "
                    f"{config.move_direction_lookback}d change <= {config.max_move_change:+.1f}"
                )
            if config.use_tnx_direction_filter:
                print(
                    f"  TNX rate-momentum filter: {config.tnx_ticker} "
                    f"{config.tnx_direction_lookback}d % change"
                    f" <= {config.max_tnx_change:+.1f}%"
                )
            if config.use_xlu_depth_filter:
                print(
                    f"  XLU capitulation-depth floor: XLU "
                    f"{config.xlu_depth_lookback}d return"
                    f" >= {config.min_xlu_return:+.1%}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

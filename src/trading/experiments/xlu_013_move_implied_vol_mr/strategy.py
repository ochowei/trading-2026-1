"""XLU MOVE Implied-Vol Forward-Looking Regime-Gated MR 策略 (XLU-013)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_013_move_implied_vol_mr.config import (
    XLU013Config,
    create_default_config,
)
from trading.experiments.xlu_013_move_implied_vol_mr.signal_detector import (
    XLU013SignalDetector,
)


class XLU013Strategy(ExecutionModelStrategy):
    """XLU-013：XLU-012 Att3 框架 + ^MOVE forward-looking implied vol regime gate"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU013Config):
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
            print(
                f"  MOVE implied-vol gate: {config.move_ticker} Close"
                f" <= {config.max_move_level:.1f}"
            )
            if config.use_move_direction_filter:
                print(
                    f"  MOVE direction filter: {config.move_ticker} "
                    f"{config.move_direction_lookback}d change <= {config.max_move_change:+.1f}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)

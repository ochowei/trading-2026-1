"""TLT MOVE Implied-Vol Forward-Looking Regime-Gated MR 策略 (TLT-013)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_013_move_implied_vol_mr.config import (
    TLT013Config,
    create_default_config,
)
from trading.experiments.tlt_013_move_implied_vol_mr.signal_detector import (
    TLT013SignalDetector,
)


class TLT013MoveImpliedVolMRStrategy(ExecutionModelStrategy):
    """TLT-013：BB-width + ^MOVE forward-looking implied vol regime gate MR"""

    slippage_pct: float = 0.001  # 0.1%（TLT 高流動 ETF）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT013Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  BB regime gate: BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            print(
                f"  MOVE implied-vol gate: {config.move_ticker} Close <= {config.max_move_level:.1f}"
            )
            if config.use_move_direction_filter:
                print(
                    f"  MOVE direction filter: {config.move_ticker} "
                    f"{config.move_direction_lookback}d change <= 0"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

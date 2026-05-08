"""TLT ^MOVE Multi-Window IV Direction Regime-Gated MR 策略 (TLT-016)"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tlt_016_move_multi_window_direction_mr.config import (
    TLT016Config,
    create_default_config,
)
from trading.experiments.tlt_016_move_multi_window_direction_mr.signal_detector import (
    TLT016SignalDetector,
)


class TLT016MoveMultiWindowDirectionMRStrategy(ExecutionModelStrategy):
    """TLT-016: BB-width + ^MOVE LEVEL + TLT-SPY divergence + ^MOVE multi-window
    IV direction regime gate MR (cross-strategy port from USO-028 Att1)."""

    slippage_pct: float = 0.001  # 0.1% (TLT 高流動 ETF)

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TLT016SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TLT016Config):
            print(
                f"  回檔範圍 (Pullback range): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%} ~ {abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  BB regime gate: BB({config.bb_period}, {config.bb_std}) width"
                f" / Close < {config.max_bb_width_ratio:.1%}"
            )
            print(f"  ^MOVE LEVEL gate: {config.move_ticker} Close <= {config.max_move_level:.1f}")
            print(
                f"  Cross-asset divergence: TLT vs {config.benchmark_ticker}"
                f" {config.divergence_lookback}d return diff >="
                f" {config.min_relative_return:+.1%}"
            )
            if config.use_move_5d_direction_filter:
                print(
                    f"  ^MOVE 5d direction gate: {config.move_5d_lookback}d"
                    f" change <= {config.max_move_5d_change:+.1f}"
                )
            if config.use_move_3d_direction_filter:
                print(
                    f"  ^MOVE 3d direction gate: {config.move_3d_lookback}d"
                    f" change <= {config.max_move_3d_change:+.1f}"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

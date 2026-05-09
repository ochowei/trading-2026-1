"""TQQQ-024: Post-Capitulation Vol-Transition Mean Reversion Strategy

Repo 首次「完全替代 framework」於 TQQQ：脫離 -15% extreme capitulation buy 結構，
改用 BB 下軌 + 中度 pullback + WR 深度超賣 + ClosePos 反轉 + ATR vol-transition
+ 2DD floor 的混合進場框架（cross-asset port from EWJ-005 / EEM-014 / IBIT-009）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_024_vol_transition_mr.config import (
    TQQQ024Config,
    create_default_config,
)
from trading.experiments.tqqq_024_vol_transition_mr.signal_detector import (
    TQQQ024SignalDetector,
)


class TQQQ024VolTransitionMRStrategy(ExecutionModelStrategy):
    """TQQQ Post-Capitulation Vol-Transition MR (TQQQ-024)"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ024SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ024Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ024Config):
            super()._print_strategy_params(config)
            return

        print(f"  Bollinger Bands:                BB({config.bb_period}, {config.bb_std}) 下軌觸及")
        print(
            f"  回檔範圍 (Pullback range):       {config.pullback_lookback}日 ∈ "
            f"[{config.pullback_cap:.0%}, {config.pullback_floor:.0%}]"
        )
        print(f"  Williams %R:                    WR({config.wr_period}) <= {config.wr_threshold}")
        print(
            f"  收盤強反轉 (ClosePos):          >= {config.close_position_threshold:.0%} of day range"
        )
        print(
            f"  ATR vol-transition:             ATR({config.atr_short_period})/"
            f"ATR({config.atr_long_period}) > {config.atr_ratio_threshold}"
        )
        print(f"  2 日累計報酬下限 (2DD floor):   <= {config.twoday_return_floor:.1%}")
        print(f"  獲利目標 (Profit target):       +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):               {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):         {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):              {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                {config.slippage_pct:.1%}")

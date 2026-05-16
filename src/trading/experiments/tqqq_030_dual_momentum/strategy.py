"""TQQQ-030 TQQQ Dual-Horizon Momentum Continuation 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_030_dual_momentum.config import (
    TQQQ030Config,
    create_default_config,
)
from trading.experiments.tqqq_030_dual_momentum.signal_detector import (
    TQQQ030SignalDetector,
)


class TQQQ030DualMomentumStrategy(ExecutionModelStrategy):
    """TQQQ-030：TQQQ 自身雙時框動量堆疊（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ030SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ030Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ030Config):
            super()._print_strategy_params(config)
            return

        print("  訊號來源 (Signal source):        TQQQ 自身 (3x leveraged)")
        print(
            f"  短時框動量:                     ROC({config.roc_short_period}) > "
            f"{config.roc_short_threshold:.1f}%"
        )
        print(
            f"  中時框動量:                     ROC({config.roc_medium_period}) > "
            f"{config.roc_medium_threshold:.1f}%"
        )
        print(f"  趨勢確認 (Trend):               Close > SMA({config.trend_sma_period})")
        if config.use_bull_filter:
            print(f"  Bull regime 過濾:               Close > SMA({config.bull_sma_period})")
        if config.use_vol_cap:
            print(
                f"  波動率上限 (Vol cap):           BB width/Close < "
                f"{config.max_bb_width_ratio:.2f}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")

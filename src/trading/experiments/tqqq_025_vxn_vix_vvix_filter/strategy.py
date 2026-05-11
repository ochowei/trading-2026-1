"""TQQQ-025 VXN-VIX Cross-Index Divergence + VVIX Direction Filter 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_025_vxn_vix_vvix_filter.config import (
    TQQQ025Config,
    create_default_config,
)
from trading.experiments.tqqq_025_vxn_vix_vvix_filter.signal_detector import (
    TQQQ025SignalDetector,
)


class TQQQ025VxnVixVvixStrategy(ExecutionModelStrategy):
    """TQQQ-025：TQQQ-018 框架 + VXN/VIX 比率 + VVIX 方向 filter（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ025SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ025Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ025Config):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(
            f"  波動率閘門 (Vol Regime Gate):    BB({config.bb_period}, {config.bb_std}) width"
            f" / Close < {config.max_bb_width_ratio:.2f}"
        )
        print(
            f"  進場前回撤 (Prior DD Filter):    DD(T-{config.prior_drawdown_lookback}) "
            f"<= {config.prior_drawdown_threshold:.0%}"
        )
        if config.use_vxn_vix_filter:
            print(
                f"  VXN/VIX 比率下限:               "
                f"{config.vxn_ticker}/{config.vix_ticker} ratio >= "
                f"{config.min_vxn_vix_ratio:.3f}"
            )
        if config.use_vvix_direction_filter:
            print(
                f"  VVIX 方向下限:                  "
                f"{config.vvix_ticker} {config.vvix_direction_lookback}d cum change "
                f">= {config.min_vvix_direction_change:+.2f}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")

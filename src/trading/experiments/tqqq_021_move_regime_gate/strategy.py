"""TQQQ-021 ^MOVE Bond-Vol LEVEL Regime Gate on Vol-Regime-Gated Capitulation Buy 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_021_move_regime_gate.config import (
    TQQQ021Config,
    create_default_config,
)
from trading.experiments.tqqq_021_move_regime_gate.signal_detector import (
    TQQQ021SignalDetector,
)


class TQQQ021MoveRegimeStrategy(ExecutionModelStrategy):
    """TQQQ-021：TQQQ-018 框架 + ^MOVE LEVEL filter（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ021SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ021Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ021Config):
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
        print(
            f"  ^MOVE LEVEL cap (bond vol):      {config.move_ticker} "
            f"close <= {config.max_move_level:.1f}"
        )
        if config.use_move_direction_filter:
            print(
                f"  ^MOVE DIRECTION cap:             "
                f"{config.move_direction_lookback}d cumulative change "
                f"<= {config.max_move_direction_change:+.2f}"
            )
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")

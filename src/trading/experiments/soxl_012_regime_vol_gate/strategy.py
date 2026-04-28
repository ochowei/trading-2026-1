"""SOXL-012 Volatility-Regime-Gated Capitulation Buy 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_012_regime_vol_gate.config import (
    SOXL012Config,
    create_default_config,
)
from trading.experiments.soxl_012_regime_vol_gate.signal_detector import (
    SOXL012SignalDetector,
)


class SOXL012RegimeVolGateStrategy(ExecutionModelStrategy):
    """SOXL-012：波動率 regime 閘門 + 精選超賣（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXL012SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXL012Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXL012Config):
            super()._print_strategy_params(config)
            return

        print(f"  回撤下限 (Drawdown threshold):   {config.drawdown_threshold:.0%}")
        print(f"  回撤上限 (Drawdown cap):          {config.drawdown_cap:.0%}")
        print(f"  2日跌幅 (2-day drop):             ≤ {config.drop_2d_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):   RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(
            f"  波動率閘門 (Vol Regime Gate):    BB({config.bb_period}, {config.bb_std}) width"
            f" / Close < {config.max_bb_width_ratio:.2f}"
        )
        if config.enable_prior_drawdown_filter:
            print(
                f"  進場前回撤 (Prior DD Filter):    DD(T-{config.prior_drawdown_lookback}) "
                f"<= {config.prior_drawdown_threshold:.0%}"
            )
        print(f"  獲利目標 (Profit target):         +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                 {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):           {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):                {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                  {config.slippage_pct:.1%}")

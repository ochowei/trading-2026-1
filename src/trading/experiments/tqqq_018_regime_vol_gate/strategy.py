"""TQQQ-018 Volatility-Regime-Gated Capitulation Buy 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_018_regime_vol_gate.config import (
    TQQQ018Config,
    create_default_config,
)
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)


class TQQQ018RegimeVolGateStrategy(ExecutionModelStrategy):
    """TQQQ-018：波動率 regime 閘門 + 恐慌抄底（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ018SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ018Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ018Config):
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
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")

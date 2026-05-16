"""TQQQ-029 TQQQ Donchian Channel Trend-Following 策略"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_029_donchian_trend.config import (
    TQQQ029Config,
    create_default_config,
)
from trading.experiments.tqqq_029_donchian_trend.signal_detector import (
    TQQQ029SignalDetector,
)


class TQQQ029DonchianTrendStrategy(ExecutionModelStrategy):
    """TQQQ-029：Donchian 通道趨勢跟蹤（含成交模型）

    成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQ029SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQ029Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQ029Config):
            super()._print_strategy_params(config)
            return

        print("  訊號來源 (Signal source):        TQQQ 自身 (3x leveraged)")
        print(f"  Donchian 突破:                  Close > 前 {config.donchian_period} 日 High max")
        print(f"  趨勢確認 (Trend):               Close > SMA({config.trend_sma_period})")
        if config.use_bull_filter:
            print(f"  Bull regime 過濾:               Close > SMA({config.bull_sma_period})")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")
        print(f"  滑價 (Slippage):                 {config.slippage_pct:.1%}")

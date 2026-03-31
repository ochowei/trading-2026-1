"""
SOXL 優化出場 + 成交模型策略 (SOXL Optimized Exit + Execution Model Strategy)
基於 SOXL-005，調整持倉天數與冷卻期。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_006_optimized_exit.config import (
    SOXL006Config,
    create_default_config,
)
from trading.experiments.soxl_006_optimized_exit.signal_detector import (
    SOXL006SignalDetector,
)


class SOXL006Strategy(ExecutionModelStrategy):
    """
    SOXL 優化出場 + 成交模型策略 (SOXL-006)

    訊號邏輯: 回撤範圍 [-40%, -25%] + RSI(5) < 25 + 2日急跌 ≤ -8%
    出場: TP +18% / SL -12% / 15 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXL006SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXL006Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXL006Config):
            super()._print_strategy_params(config)
            return

        print(f"  回撤下限 (Drawdown threshold):   {config.drawdown_threshold:.0%}")
        print(f"  回撤上限 (Drawdown cap):          {config.drawdown_cap:.0%}")
        print(f"  2日跌幅 (2-day drop):             ≤ {config.drop_2d_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):   RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  獲利目標 (Profit target):         +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                 {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):           {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):                {config.cooldown_days} 天")

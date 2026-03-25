"""
TQQQ 優化出場 + 成交模型策略 (TQQQ Optimized Exit + Execution Model Strategy)
重做 TQQQ-008：保持基線三條件進場 + 優化出場，加入成交模型以貼近實盤。
Redo of TQQQ-008 with realistic execution model (next_open entry, stop_market, limit_order, slippage).
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tqqq_cap_exec_optimized.config import (
    TQQQCapExecOptimizedConfig,
    create_default_config,
)
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector


class TQQQCapExecOptimizedStrategy(ExecutionModelStrategy):
    """
    TQQQ 優化出場 + 成交模型策略 (TQQQ-010)

    訊號邏輯: 與 TQQQ-008 完全相同（基線三條件進場 + 優化出場）
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    Signal logic: Identical to TQQQ-008 (baseline 3-condition entry + optimized exit)
    Execution model: next_open_market entry, limit_order profit, stop_market stop, pessimistic
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001  # 0.1%
        if isinstance(config, TQQQCapExecOptimizedConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapExecOptimizedConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")

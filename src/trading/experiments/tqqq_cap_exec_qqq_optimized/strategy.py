"""
TQQQ QQQ 相對強度確認 + 優化出場 + 成交模型策略
(TQQQ QQQ Confirmation + Optimized Exit + Execution Model Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.experiments.tqqq_cap_exec_qqq_confirm.strategy import TQQQCapExecQqqConfirmStrategy
from trading.experiments.tqqq_cap_exec_qqq_optimized.config import (
    TQQQCapExecQqqOptimizedConfig,
    create_default_config,
)
from trading.experiments.tqqq_cap_qqq_confirm.signal_detector import TQQQCapQqqConfirmDetector


class TQQQCapExecQqqOptimizedStrategy(TQQQCapExecQqqConfirmStrategy):
    """TQQQ-013: QQQ RSI 過濾 + 優化出場 + 成交模型。"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQCapQqqConfirmDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, TQQQCapExecQqqOptimizedConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TQQQCapExecQqqOptimizedConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  QQQ RSI 過濾 (QQQ RSI filter):  RSI({config.qqq_rsi_period}) < {config.qqq_rsi_threshold}")
        print(f"  冷卻天數 (Cooldown):             {config.cooldown_days} 天")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

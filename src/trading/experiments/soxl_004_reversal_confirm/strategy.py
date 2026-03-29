"""
SOXL 反轉確認 + 成交模型策略 (SOXL Reversal Confirm + Execution Model Strategy)
基於 SOXL-003，以 ClosePos 反轉確認取代成交量過濾。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_004_reversal_confirm.config import (
    SOXLReversalConfirmConfig,
    create_default_config,
)
from trading.experiments.soxl_004_reversal_confirm.signal_detector import (
    SOXLReversalConfirmSignalDetector,
)


class SOXLReversalConfirmStrategy(ExecutionModelStrategy):
    """
    SOXL 反轉確認 + 成交模型策略 (SOXL-004)

    訊號邏輯: 三條件進場（回撤 ≥ 25% + RSI < 25 + ClosePos ≥ 35%）
    出場: TP +18% / SL -12% / 20 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLReversalConfirmSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXLReversalConfirmConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXLReversalConfirmConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  收盤位置 (Close position min):   ≥ {config.close_position_min:.0%}")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")

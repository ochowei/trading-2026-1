"""
SOXL 寬停損 + 成交模型策略 (SOXL Wide SL + Execution Model Strategy)
基於 SOXL-002，放寬停損並延長持倉。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_003_wide_sl.config import (
    SOXLWideSLConfig,
    create_default_config,
)
from trading.experiments.soxl_003_wide_sl.signal_detector import (
    SOXLWideSLSignalDetector,
)


class SOXLWideSLStrategy(ExecutionModelStrategy):
    """
    SOXL 寬停損 + 成交模型策略 (SOXL-003)

    訊號邏輯: 三條件進場（回撤 ≥ 25% + RSI < 25 + 成交量放大）
    出場: TP +15% / SL -15% / 20 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLWideSLSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXLWideSLConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXLWideSLConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):               {config.cooldown_days} 天")

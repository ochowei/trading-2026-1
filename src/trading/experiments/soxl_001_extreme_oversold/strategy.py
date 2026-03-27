"""
SOXL 極端超賣 + 成交模型策略 (SOXL Extreme Oversold + Execution Model Strategy)
以 TQQQ-010 為模板，針對 SOXL 波動度縮放參數，加入成交模型以貼近實盤。
Based on TQQQ-010 template, with parameters scaled for SOXL volatility and execution model.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_001_extreme_oversold.config import (
    SOXLExtremeOversoldConfig,
    create_default_config,
)
from trading.experiments.soxl_001_extreme_oversold.signal_detector import SOXLSignalDetector


class SOXLExtremeOversoldStrategy(ExecutionModelStrategy):
    """
    SOXL 極端超賣 + 成交模型策略 (SOXL-001)

    訊號邏輯: 三條件進場（回撤 ≥ 20% + RSI < 25 + 成交量放大）
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    Signal logic: 3-condition entry (drawdown >= 20% + RSI < 25 + volume spike)
    Execution model: next_open_market entry, limit_order profit, stop_market stop, pessimistic
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLSignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001  # 0.1%
        if isinstance(config, SOXLExtremeOversoldConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXLExtremeOversoldConfig):
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

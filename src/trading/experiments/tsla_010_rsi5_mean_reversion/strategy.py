"""
TSLA-010: RSI(5) Mean Reversion + 成交模型策略
TSLA RSI(5) Mean Reversion + Execution Model Strategy

改編 SOXL-006 框架至 TSLA，使用 RSI(5) 取代 RSI(2)。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_010_rsi5_mean_reversion.config import (
    TSLARSI5MeanRevConfig,
    create_default_config,
)
from trading.experiments.tsla_010_rsi5_mean_reversion.signal_detector import (
    TSLARSI5MeanRevDetector,
)


class TSLARSI5MeanRevStrategy(ExecutionModelStrategy):
    """
    TSLA RSI(5) 均值回歸 + 成交模型策略 (TSLA-010)

    訊號邏輯: 回撤範圍 [-30%, -15%] + RSI(5) < 20 + 2日急跌 ≤ -6%
    出場: TP +10% / SL -10% / 20 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLARSI5MeanRevDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.0015
        if isinstance(config, TSLARSI5MeanRevConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, TSLARSI5MeanRevConfig):
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

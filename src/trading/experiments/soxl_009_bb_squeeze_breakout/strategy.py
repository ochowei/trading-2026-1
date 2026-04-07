"""
SOXL BB 擠壓突破 + 成交模型策略
SOXL BB Squeeze Breakout + Execution Model Strategy

首次在 SOXL 上嘗試突破策略，受 TSLA-005 啟發。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_009_bb_squeeze_breakout.config import (
    SOXLBBSqueezeConfig,
    create_default_config,
)
from trading.experiments.soxl_009_bb_squeeze_breakout.signal_detector import (
    SOXLBBSqueezeDetector,
)


class SOXLBBSqueezeBreakoutStrategy(ExecutionModelStrategy):
    """
    SOXL BB 擠壓突破 + 成交模型策略 (SOXL-009)

    訊號邏輯: BB(20,2) 擠壓（60日 25th 百分位，5日內）+ Close > Upper BB + Close > SMA(50)
    出場: TP +15% / SL -10% / 20 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLBBSqueezeDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXLBBSqueezeConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXLBBSqueezeConfig):
            super()._print_strategy_params(config)
            return

        print(f"  BB 週期/標準差 (BB period/std):   BB({config.bb_period}, {config.bb_std})")
        print(
            f"  擠壓百分位 (Squeeze pctile):      {config.bb_squeeze_percentile:.0%} "
            f"over {config.bb_squeeze_percentile_window}d"
        )
        print(f"  擠壓回看 (Squeeze recent days):   {config.bb_squeeze_recent_days} 天")
        print(f"  趨勢確認 (Trend SMA):             SMA({config.sma_trend_period})")
        print(f"  獲利目標 (Profit target):         +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                 {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):           {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):                {config.cooldown_days} 天")

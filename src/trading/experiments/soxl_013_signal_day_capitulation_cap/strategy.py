"""
SOXL-013 Signal-Day Capitulation-Strength CAP MR + 成交模型策略

訊號邏輯: SOXL-006 capitulation MR（回撤 [-40%,-25%] + RSI(5)<20 + 2DD≤-8%）
          + 3 日報酬 CAP（lesson #19 family，方向經預分析校正為 3d-cap）
出場: TP +18% / SL -12% / 25 天（SOXL 硬上限，lesson #41，無 trailing）
成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_013_signal_day_capitulation_cap.config import (
    SOXL013Config,
    create_default_config,
)
from trading.experiments.soxl_013_signal_day_capitulation_cap.signal_detector import (
    SOXL013SignalDetector,
)


class SOXL013Strategy(ExecutionModelStrategy):
    """SOXL-013 Signal-Day Capitulation-Strength CAP MR 策略"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXL013SignalDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXL013Config):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXL013Config):
            super()._print_strategy_params(config)
            return

        print(f"  回撤下限 (Drawdown threshold):   {config.drawdown_threshold:.0%}")
        print(f"  回撤上限 (Drawdown cap):          {config.drawdown_cap:.0%}")
        print(f"  2日跌幅 (2-day drop):             ≤ {config.drop_2d_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):   RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(f"  3日報酬上限 (3d return cap):       >= {config.threeday_return_cap:.0%}")
        print(f"  獲利目標 (Profit target):         +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                 {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):           {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):                {config.cooldown_days} 天")

"""
SOXL-011: SOXX ATR-Adaptive Mean Reversion 策略

基於 SOXL-006 均值回歸框架，新增 SOXX ATR(5)/ATR(20) 波動率自適應過濾。
在底層指數 SOXX 波動率擴張時才接受進場訊號，過濾慢磨下跌的假訊號。

結果：三次嘗試均未超越 SOXL-006 基線（min(A,B) 0.47）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.soxl_011_soxx_atr_adaptive.config import (
    SOXLSoxxAtrConfig,
    create_default_config,
)
from trading.experiments.soxl_011_soxx_atr_adaptive.signal_detector import (
    SOXLSoxxAtrDetector,
)


class SOXLSoxxAtrStrategy(ExecutionModelStrategy):
    """
    SOXL-011: SOXX ATR-Adaptive Mean Reversion（含成交模型）

    訊號邏輯: SOXL-006 框架 + SOXX ATR(5)/ATR(20) > 1.1
    出場: TP +18% / SL -12% / 25 天
    成交模型: next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SOXLSoxxAtrDetector(create_default_config())

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        slippage = 0.001
        if isinstance(config, SOXLSoxxAtrConfig):
            slippage = config.slippage_pct
        return ExecutionModelBacktester(config, slippage_pct=slippage)

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if not isinstance(config, SOXLSoxxAtrConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤下限 (Drawdown threshold):   {config.drawdown_threshold:.0%}")
        print(f"  回撤上限 (Drawdown cap):          {config.drawdown_cap:.0%}")
        print(f"  2日跌幅 (2-day drop):             <= {config.drop_2d_threshold:.0%}")
        print(
            f"  RSI 週期/閾值 (RSI period/thr):   RSI({config.rsi_period}) < {config.rsi_threshold}"
        )
        print(
            f"  SOXX ATR 過濾 (SOXX ATR filter):  ATR({config.atr_fast_period})"
            f"/ATR({config.atr_slow_period}) > {config.atr_ratio_threshold}"
        )
        print(f"  獲利目標 (Profit target):         +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                 {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):           {config.holding_days} 天")
        print(f"  冷卻期 (Cooldown):                {config.cooldown_days} 天")

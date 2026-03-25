"""
TQQQ 恐慌抄底策略 (TQQQ Capitulation Buy Strategy)
串接配置 → 訊號偵測器 → 回測引擎。
Wires config → signal detector → backtester.
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.tqqq_capitulation.config import TQQQConfig, create_default_config
from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector


class TQQQStrategy(BaseStrategy):
    """
    TQQQ 恐慌抄底策略 (TQQQ Capitulation Buy Strategy)

    專為 TQQQ 設計的低頻高勝率策略，每年約 3-5 次訊號。
    Low-frequency, high-win-rate strategy designed for TQQQ, ~3-5 signals/year.
    """

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TQQQSignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        """印出 TQQQ 專屬策略參數"""
        if not isinstance(config, TQQQConfig):
            super()._print_strategy_params(config)
            return

        print(f"  回撤閾值 (Drawdown threshold):  {config.drawdown_threshold:.0%}")
        print(f"  RSI 週期/閾值 (RSI period/thr):  RSI({config.rsi_period}) < {config.rsi_threshold}")
        print(f"  成交量倍數 (Volume multiplier):  {config.volume_multiplier}x")
        print(f"  獲利目標 (Profit target):        +{config.profit_target:.0%}")
        print(f"  停損 (Stop-loss):                {config.stop_loss:.0%}")
        print(f"  最長持倉 (Max holding):          {config.holding_days} 天")

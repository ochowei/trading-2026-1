"""
XBI-012: Capitulation + Acceleration Reversal 策略
(XBI Capitulation + Acceleration Reversal Mean Reversion Strategy)
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_012_capitulation_accel.config import (
    XBI012Config,
    create_default_config,
)
from trading.experiments.xbi_012_capitulation_accel.signal_detector import (
    XBI012SignalDetector,
)


class XBI012Strategy(ExecutionModelStrategy):
    """XBI-012: 短期急跌 + 中點反攻均值回歸"""

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI012Config):
            print(
                f"  Pullback 環境: {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(
                f"  短期急跌 (ROC): {config.roc_lookback} 日 ROC <= "
                f"{config.roc_threshold:.0%}"
            )
            print(
                f"  日內反攻: ClosePos >= {config.close_position_threshold:.0%}"
                f" + Up Day = {config.require_up_day}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)

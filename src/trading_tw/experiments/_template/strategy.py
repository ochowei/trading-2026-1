"""
<實驗名稱> 策略 (<Experiment Name> Strategy)
串接配置 → 訊號偵測器 → 回測引擎。
"""

from trading_tw.core.base_config import ExperimentConfig
from trading_tw.core.base_signal_detector import BaseSignalDetector
from trading_tw.core.base_strategy import BaseStrategy

# from trading_tw.experiments.<your_experiment>.config import create_default_config
# from trading_tw.experiments.<your_experiment>.signal_detector import MySignalDetector


class MyStrategy(BaseStrategy):
    """自訂策略 (Custom strategy)"""

    def create_config(self) -> ExperimentConfig:
        # return create_default_config()
        raise NotImplementedError("請實作 create_config()")

    def create_detector(self) -> BaseSignalDetector:
        # return MySignalDetector(create_default_config())
        raise NotImplementedError("請實作 create_detector()")

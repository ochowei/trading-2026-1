"""
<實驗名稱> 訊號偵測模組 (<Experiment Name> Signal Detector)
計算技術指標並偵測交易訊號。
"""

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector

# from trading.experiments.<your_experiment>.config import MyConfig


class MySignalDetector(BaseSignalDetector):
    """自訂訊號偵測器 (Custom signal detector)"""

    def __init__(self, config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標 (Compute technical indicators)"""
        df = df.copy()
        # 在此計算指標 (Compute your indicators here)
        # 例如: df["SMA20"] = df["Close"].rolling(20).mean()
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測交易訊號 (Detect trading signals)"""
        df = df.copy()
        # 在此定義訊號邏輯 (Define your signal logic here)
        # df["Signal"] = <your conditions>
        df["Signal"] = False  # 預設無訊號
        return df

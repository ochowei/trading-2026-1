"""
訊號偵測基礎類別 (Base Signal Detector)
所有實驗的訊號偵測器都繼承此 ABC。
All experiment signal detectors inherit from this ABC.
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseSignalDetector(ABC):
    """訊號偵測器基礎類別 (Base class for signal detectors)"""

    @abstractmethod
    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算技術指標 (Compute technical indicators)

        在完整資料上計算，避免 rolling 邊界問題。
        Must not drop rows. Compute on full data to avoid rolling boundary issues.

        Args:
            df: OHLCV DataFrame

        Returns:
            df with indicator columns added
        """
        ...

    @abstractmethod
    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測交易訊號 (Detect trading signals)

        必須新增布林欄位 'Signal'。
        Must add a boolean 'Signal' column to df.

        Args:
            df: DataFrame with indicators already computed

        Returns:
            df with 'Signal' boolean column added
        """
        ...

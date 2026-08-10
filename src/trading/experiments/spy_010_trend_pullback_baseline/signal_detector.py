"""SPY-010 family baseline: SPY-007 Attempt 2 momentum pullback.

進場條件（全部滿足）：
1. Close > SMA(200)
2. SMA(20) > SMA(50)
3. Low <= SMA(20)
4. Close > SMA(20)
5. 冷卻期 10 個交易日

The baseline deliberately has no ClosePos filter. Adding that filter and extending the
cooldown to 15 sessions defines the selected SPY-007 Attempt 3 trial.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.spy_010_trend_pullback_baseline.config import (
    SPY010TrendPullbackBaselineConfig,
)

logger = logging.getLogger(__name__)


class SPY010TrendPullbackBaselineDetector(BaseSignalDetector):
    """偵測未加 ClosePos confirmation 的 SMA(20) 趨勢回檔訊號。"""

    def __init__(self, config: SPY010TrendPullbackBaselineConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算完整資料上的三條固定 SMA。"""
        df = df.copy()
        df["SMA_Short"] = df["Close"].rolling(self.config.sma_short_period).mean()
        df["SMA_Mid"] = df["Close"].rolling(self.config.sma_mid_period).mean()
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """套用 Attempt 2 entry gates 與十個交易日 cooldown。"""
        df = df.copy()
        df["Signal"] = (
            (df["Close"] > df["SMA_Long"])
            & (df["SMA_Short"] > df["SMA_Mid"])
            & (df["Low"] <= df["SMA_Short"])
            & (df["Close"] > df["SMA_Short"])
        )

        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None
        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx
        if suppressed:
            df.loc[suppressed, "Signal"] = False

        logger.info(
            "SPY-010: Detected %d trend-pullback baseline signals",
            df["Signal"].sum(),
        )
        return df

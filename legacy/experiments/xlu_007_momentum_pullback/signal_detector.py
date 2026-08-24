"""
XLU-007 訊號偵測器：XLU/SPY Pairs Trading
XLU-007 Signal Detector: XLU-SPY Pairs Trading

進場條件（全部滿足）：
1. XLU/SPY 比值 z-score(40) < -1.5（XLU 相對 SPY 顯著落後）
2. XLU 收盤價 > SMA(50)（XLU 長期趨勢向上，非結構性崩潰）
3. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.xlu_007_momentum_pullback.config import XLU007Config

logger = logging.getLogger(__name__)


class XLU007Detector(DeclaredAuxiliaryData, BaseSignalDetector):
    """XLU-SPY Pairs Trading 訊號偵測器"""

    def __init__(self, config: XLU007Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return ("SPY",)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SPY data comes from the verified auxiliary bundle.
        spy = self.require_auxiliary("SPY", df.index)

        # XLU/SPY ratio
        ratio = df["Close"] / spy["Close"]
        df["Ratio"] = ratio

        # Z-score of ratio
        lookback = self.config.zscore_lookback
        ratio_mean = ratio.rolling(lookback).mean()
        ratio_std = ratio.rolling(lookback).std()
        df["Ratio_ZScore"] = (ratio - ratio_mean) / ratio_std

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # XLU underperforming SPY: z-score below threshold
        cond_zscore = df["Ratio_ZScore"] < self.config.zscore_threshold

        # XLU long-term trend intact
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_zscore & cond_trend

        # Cooldown mechanism
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

        signal_count = df["Signal"].sum()
        logger.info("XLU-007: Detected %d XLU/SPY pairs trading signals", signal_count)
        return df

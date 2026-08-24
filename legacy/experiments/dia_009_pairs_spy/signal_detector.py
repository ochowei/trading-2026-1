"""
DIA-009 訊號偵測器：Pairs Trading (DIA/SPY)
DIA-009 Signal Detector: DIA/SPY Pairs Trading

進場條件（全部滿足）：
1. DIA/SPY 價格比值的 60日 z-score < -2.5（DIA 相對低估）
2. Close > SMA(50)（趨勢確認，排除結構性下跌）
3. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.dia_009_pairs_spy.config import DIAPairsSPYConfig

logger = logging.getLogger(__name__)


class DIAPairsSPYDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """DIA/SPY Pairs Trading 訊號偵測器"""

    def __init__(self, config: DIAPairsSPYConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.pair_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        spy_df = self.require_auxiliary(self.config.pair_ticker, df.index)

        # 計算對數價格比值（log ratio 更穩定）
        df["Price_Ratio"] = np.log(df["Close"] / spy_df["Close"])

        # 滾動 z-score
        lookback = self.config.zscore_lookback
        rolling_mean = df["Price_Ratio"].rolling(lookback).mean()
        rolling_std = df["Price_Ratio"].rolling(lookback).std()
        df["Ratio_Zscore"] = (df["Price_Ratio"] - rolling_mean) / rolling_std

        # SMA 趨勢確認
        df["SMA"] = df["Close"].rolling(self.config.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # z-score 低於閾值（DIA 相對低估）+ 趨勢確認
        df["Signal"] = (df["Ratio_Zscore"] < self.config.zscore_entry) & (df["Close"] > df["SMA"])

        # 冷卻機制
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
        logger.info("DIA: Detected %d pairs trading signals", signal_count)
        return df

"""
XBI-008 訊號偵測器：Pairs Trading (XBI/IBB)

進場條件（全部滿足）：
1. XBI/IBB 對數價格比值的 60日 z-score < -2.0（XBI 相對低估）
2. Close > SMA(50)（趨勢確認，排除結構性下跌）
3. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.xbi_008_pairs_ibb.config import XBI008Config

logger = logging.getLogger(__name__)


class XBIPairsIBBDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """XBI/IBB Pairs Trading 訊號偵測器"""

    def __init__(self, config: XBI008Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.pair_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        ibb_close = self.require_auxiliary(self.config.pair_ticker, df.index)["Close"]
        df["Price_Ratio"] = np.log(df["Close"] / ibb_close)

        lookback = self.config.zscore_lookback
        rolling_mean = df["Price_Ratio"].rolling(lookback).mean()
        rolling_std = df["Price_Ratio"].rolling(lookback).std()
        df["Ratio_Zscore"] = (df["Price_Ratio"] - rolling_mean) / rolling_std

        df["SMA"] = df["Close"].rolling(self.config.sma_period).mean()

        if self.config.use_wr_filter:
            highest = df["High"].rolling(self.config.wr_period).max()
            lowest = df["Low"].rolling(self.config.wr_period).min()
            df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        else:
            df["WR"] = 0.0

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        zscore_cond = df["Ratio_Zscore"] < self.config.zscore_entry

        cond = zscore_cond
        if self.config.use_sma_filter:
            cond = cond & (df["Close"] > df["SMA"])
        if self.config.use_wr_filter:
            cond = cond & (df["WR"] <= self.config.wr_threshold)

        df["Signal"] = cond

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
        logger.info("XBI: Detected %d pairs trading signals", signal_count)
        return df

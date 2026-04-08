"""
XLU-010 訊號偵測器：20日寬回檔 + Williams %R + 反轉K線

進場條件（全部滿足）：
1. 20 日回檔 >= 5% 且 <= 10%（寬回檔範圍，過濾淺回檔+極端崩盤）
2. Williams %R(10) <= -80（超賣確認）
3. 收盤位置 >= 40%（日內反轉確認）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_010_20d_wide_pullback.config import (
    XLU20dWidePullbackConfig,
)

logger = logging.getLogger(__name__)


class XLU20dWidePullbackSignalDetector(BaseSignalDetector):
    def __init__(self, config: XLU20dWidePullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 20 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback & cond_cap & cond_wr & cond_reversal

        # Cooldown
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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
        logger.info("XLU-010: Detected %d 20d wide pullback + WR signals", signal_count)
        return df

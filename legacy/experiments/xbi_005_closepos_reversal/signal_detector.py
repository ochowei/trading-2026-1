"""
XBI-005 訊號偵測器：回檔 + Williams %R + 反轉K線均值回歸
(XBI-005 Signal Detector: Pullback + Williams %R + Reversal Candlestick)

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 8-20%
2. Williams %R(10) <= -80（超賣確認）
3. ClosePos >= 40%（日內反轉確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_005_closepos_reversal.config import XBI005Config

logger = logging.getLogger(__name__)


class XBI005SignalDetector(BaseSignalDetector):
    """
    XBI 回檔 + Williams %R + 反轉K線訊號偵測器

    四條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 >= 8%
    2. 回檔幅度 <= 20%（過濾極端崩盤）
    3. Williams %R(10) <= -80（超賣）
    4. ClosePos >= 40%（日內反轉確認）
    """

    def __init__(self, config: XBI005Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件四：反轉K線確認
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        # 四條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_reversal

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
            logger.info(
                "XBI-005: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("XBI-005: Detected %d Pullback+WR+Reversal signals", signal_count)
        return df

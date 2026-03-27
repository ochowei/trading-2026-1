"""
FCX 回檔 + Williams %R + 反轉K線訊號偵測器
FCX Pullback + Williams %R + Reversal Candle Signal Detector

改編自 GLD-007 已驗證的三重條件進場邏輯，參數依 FCX 波動特性縮放。

進場條件（全部滿足）：
1. 收盤價低於 10 日高點 >= 9%（回檔確認）
2. Williams %R(10) <= -80（超賣確認）
3. 收盤位置 >= 40%（反轉K線確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_002_pullback_wr.config import FCXPullbackWRConfig

logger = logging.getLogger(__name__)


class FCXPullbackWRDetector(BaseSignalDetector):
    """FCX 回檔 + Williams %R + 反轉K線訊號偵測器"""

    def __init__(self, config: FCXPullbackWRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. 回檔幅度：從 N 日高點的跌幅
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # 2. Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 3. 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        # 若 High == Low（零振幅），設為 0.5（中性）
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 三重條件
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback & cond_wr & cond_reversal

        # 冷卻期：抑制間隔太近的訊號
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
        logger.info("FCX: Detected %d Pullback+WR+Reversal signals", signal_count)
        return df

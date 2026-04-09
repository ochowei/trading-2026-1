"""
COPX-007 訊號偵測器：波動率自適應 20日回檔 + Williams %R 均值回歸

進場條件（全部滿足）：
1. 收盤價相對 20 日最高價回檔 10-20%
2. Williams %R(10) <= -80（超賣確認）
3. ATR(5) / ATR(20) > 1.1（波動率飆升，過濾慢磨下跌）
4. 冷卻期 12 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_007_vol_adaptive.config import COPX007Config

logger = logging.getLogger(__name__)


class COPX007SignalDetector(BaseSignalDetector):
    """COPX-007 波動率自適應均值回歸訊號偵測器"""

    def __init__(self, config: COPX007Config):
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

        # ATR ratio: short-term vs long-term volatility
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件四：波動率飆升（ATR ratio）
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        # 四條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_vol

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
                "COPX-007: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("COPX-007: Detected %d vol-adaptive pullback+WR signals", signal_count)
        return df

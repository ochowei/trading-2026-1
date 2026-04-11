"""
TQQQ-016 訊號偵測器：回檔 + Williams %R + 成交量放大均值回歸
(TQQQ-016 Signal Detector: Pullback + Williams %R + Volume Spike Mean Reversion)

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 18-30%（過濾淺回檔與極端崩盤）
2. Williams %R(10) <= -80（超賣確認）
3. 成交量 > 1.5x 20 日均量（恐慌賣壓確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_016_pullback_wr.config import TQQQPullbackWRConfig

logger = logging.getLogger(__name__)


class TQQQPullbackWRSignalDetector(BaseSignalDetector):
    """TQQQ 回檔 + Williams %R + 成交量放大訊號偵測器"""

    def __init__(self, config: TQQQPullbackWRConfig):
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

        # 成交量均線
        df["Volume_SMA"] = df["Volume"].rolling(self.config.volume_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件四：成交量放大（恐慌賣壓確認）
        cond_volume = df["Volume"] > self.config.volume_multiplier * df["Volume_SMA"]

        # 四條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_volume

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
            logger.info("TQQQ: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TQQQ: Detected %d Pullback+WR+Volume reversion signals", signal_count)
        return df

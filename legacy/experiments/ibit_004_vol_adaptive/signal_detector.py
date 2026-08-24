"""
IBIT-004 訊號偵測器：波動率自適應 / 2日急跌回檔 + Williams %R 均值回歸

Att1/Att2: ATR(5)/ATR(20) 過濾（失敗，IBIT 日波動 3.17% 超出有效邊界）
Att3: 2日急跌 ≤ -5%（USO-013 模式，選擇恐慌性急跌而非慢磨下跌）

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 12-22%
2. Williams %R(10) <= -80（超賣確認）
3. 2日跌幅 ≤ -5%（急跌確認）
4. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ibit_004_vol_adaptive.config import IBIT004Config

logger = logging.getLogger(__name__)


class IBIT004SignalDetector(BaseSignalDetector):
    """IBIT-004 波動率自適應 / 2日急跌均值回歸訊號偵測器"""

    def __init__(self, config: IBIT004Config):
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

        # 2日跌幅
        df["TwoDayDrop"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度下限
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：回檔幅度上限（過濾極端崩盤）
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件三：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件四：2日急跌
        cond_drop = df["TwoDayDrop"] <= self.config.two_day_drop_threshold

        # 四條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_drop

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
                "IBIT-004: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("IBIT-004: Detected %d pullback+WR+2d-drop signals", signal_count)
        return df

"""
CIBR 波動率自適應均值回歸訊號偵測器

在 CIBR-001（回檔+WR）基礎上新增兩個過濾器：
1. ATR(5)/ATR(20) > 1.15 — 近期波動率急升，確認為恐慌拋售而非慢磨下跌
2. ClosePos >= 40% — 日內收盤位置確認反轉跡象（收盤不在最低點附近）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_002_vol_adaptive_mr.config import CIBRVolAdaptiveMRConfig

logger = logging.getLogger(__name__)


class CIBRVolAdaptiveMRSignalDetector(BaseSignalDetector):
    """
    CIBR 波動率自適應均值回歸訊號偵測器

    四條件同時成立時觸發訊號：
    1. 收盤價相對 10 日最高價回檔 >= 5%
    2. Williams %R(10) <= -80（超賣）
    3. ClosePos >= 40%（日內反轉確認）
    4. ATR(5)/ATR(20) > 1.15（波動率急升）
    """

    def __init__(self, config: CIBRVolAdaptiveMRConfig):
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

        # Close Position：(Close - Low) / (High - Low)
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：回檔幅度
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件二：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件三：收盤位置確認反轉
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold

        # 條件四：波動率急升
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        # 四條件同時成立
        df["Signal"] = cond_pullback & cond_wr & cond_closepos & cond_atr

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
            logger.info("CIBR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR: Detected %d Vol-Adaptive Pullback+WR signals", signal_count)
        return df

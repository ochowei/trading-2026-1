"""
URA-007 訊號偵測器：波動率自適應回檔 + RSI(2) + 2日急跌均值回歸

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 10-20%
2. RSI(2) < 15（短週期超賣確認）
3. 2 日跌幅 ≤ -3%（近期恐慌確認）
4. ATR(5)/ATR(20) > 1.05（波動率飆升，過濾慢磨下跌）
5. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_007_vol_adaptive.config import URA007Config

logger = logging.getLogger(__name__)


class URA007SignalDetector(BaseSignalDetector):
    """URA-007 波動率自適應均值回歸訊號偵測器"""

    def __init__(self, config: URA007Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2) 計算
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2日跌幅
        df["TwoDayDecline"] = df["Close"].pct_change(2)

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

        # 條件三：RSI(2) 超賣
        cond_rsi = df["RSI2"] < self.config.rsi_threshold

        # 條件四：2日急跌
        cond_decline = df["TwoDayDecline"] <= self.config.two_day_decline

        # 條件五：波動率飆升（ATR ratio）
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        # 五條件同時成立
        df["Signal"] = cond_pullback & cond_upper & cond_rsi & cond_decline & cond_vol

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
            logger.info("URA-007: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "URA-007: Detected %d vol-adaptive pullback+RSI2+decline signals",
            signal_count,
        )
        return df

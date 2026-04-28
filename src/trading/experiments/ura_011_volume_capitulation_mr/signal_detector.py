"""
URA-011 訊號偵測器：成交量放大資本化均值回歸
(URA-011 Signal Detector: Volume-Confirmed Capitulation MR)

進場條件（Att3 — 移除 2DD 與 ClosePos）：
1. 10 日高點回檔 10-20%（下限/上限，沿用 URA-004）
2. RSI(2) < 15（短週期超賣，沿用 URA-004）
3. Volume(today) / Avg20(Volume) ≥ 1.5x（機構性放量，替代 2DD 功能）
4. （選用）2 日跌幅 ≤ -3%
5. （選用）ClosePos ≥ 40%
6. 冷卻期 10 個交易日
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_011_volume_capitulation_mr.config import URA011Config

logger = logging.getLogger(__name__)


class URA011SignalDetector(BaseSignalDetector):
    """URA-011 成交量放大資本化訊號偵測器"""

    def __init__(self, config: URA011Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        df["TwoDayDecline"] = df["Close"].pct_change(2)

        # 成交量比率：今日 / 過去 20 日平均
        w = self.config.volume_avg_window
        df["VolAvg"] = df["Volume"].rolling(w).mean()
        df["VolRatio"] = df["Volume"] / df["VolAvg"]

        # Close Position：當日收盤相對日內區間位置
        range_ = (df["High"] - df["Low"]).replace(0, np.nan)
        df["ClosePos"] = (df["Close"] - df["Low"]) / range_

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_volume = df["VolRatio"] >= self.config.volume_multiple

        signal = cond_pullback & cond_upper & cond_rsi & cond_volume

        if self.config.use_two_day_decline:
            signal = signal & (df["TwoDayDecline"] <= self.config.two_day_decline)
        if self.config.use_close_pos:
            signal = signal & (df["ClosePos"] >= self.config.close_pos_threshold)

        df["Signal"] = signal

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
            logger.info("URA-011: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA-011: Detected %d Volume-Confirmed Capitulation signals", signal_count)
        return df

"""
IWM-007 訊號偵測器：趨勢回檔恢復 (Attempt 3)
IWM-007 Signal Detector: Trend Pullback to SMA(50)

進場條件（全部滿足）：
1. SMA(50) 正在上升（5日 ROC > 0）
2. 收盤價 > SMA(200)（長期趨勢向上）
3. 價格接近 SMA(50)（Low 在 SMA50 的 2% 範圍內）
4. 從 10 日高點拉回至少 3%（確認有實質回檔）
5. 收盤位置 >= 50%（日內反彈確認）
6. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.iwm_007_trend_pullback.config import IWM007Config

logger = logging.getLogger(__name__)


class IWM007SignalDetector(BaseSignalDetector):
    """IWM Trend Pullback to SMA(50) 訊號偵測器"""

    def __init__(self, config: IWM007Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 中期均線 SMA(50)
        df["SMA_Mid"] = df["Close"].rolling(self.config.sma_period).mean()

        # 長期均線 SMA(200)
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        # SMA(50) 斜率
        df["SMA_Mid_Slope"] = df["SMA_Mid"].pct_change(5)

        # 10 日最高價
        df["High_10d"] = df["High"].rolling(self.config.recent_high_lookback).max()

        # 從高點的回檔幅度
        df["Pullback_Pct"] = (df["Close"] - df["High_10d"]) / df["High_10d"]

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. SMA(50) 正在上升
        cond_rising = df["SMA_Mid_Slope"] > 0

        # 2. 收盤價 > SMA(200)（長期趨勢向上）
        cond_long_trend = df["Close"] > df["SMA_Long"]

        # 3. 價格接近 SMA(50)：Low 在 SMA(50) 附近（上下 2%）
        sma_upper = df["SMA_Mid"] * (1 + self.config.proximity_pct)
        sma_lower = df["SMA_Mid"] * (1 - self.config.proximity_pct)
        cond_near_sma = (df["Low"] <= sma_upper) & (df["Close"] >= sma_lower)

        # 4. 從近期高點至少拉回 3%
        cond_pullback = df["Pullback_Pct"] <= -self.config.min_pullback_pct

        # 5. 收盤位置 >= 50%（日內反彈確認）
        cond_bounce = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_rising & cond_long_trend & cond_near_sma & cond_pullback & cond_bounce

        # Cooldown mechanism
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
        logger.info("IWM-007: Detected %d trend pullback (SMA50) signals", signal_count)
        return df

"""
SIVR Donchian 通道突破訊號偵測器 (SIVR-014)

進場條件（四條件同時成立）：
1. Close > 20 日最高 High（Donchian 通道上軌突破）
2. Close > SMA(50)（趨勢確認）
3. 最近 10 日內曾有 Close 相對 20 日高點回檔 ≥ 5%
   （確保突破來自回檔後恢復，非持續磨頂）
4. SMA(50) 上升中（SMA(50) > 20 日前的 SMA(50)）
   （Att3: 過濾熊市中 SMA 下行時的假突破）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_014_donchian_breakout.config import (
    SIVRDonchianBreakoutConfig,
)

logger = logging.getLogger(__name__)


class SIVRDonchianBreakoutSignalDetector(BaseSignalDetector):
    """SIVR Donchian 通道突破訊號偵測器"""

    def __init__(self, config: SIVRDonchianBreakoutConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.donchian_period

        # Donchian 通道上軌：N 日最高 High（不含當日）
        df["Donchian_High"] = df["High"].shift(1).rolling(n).max()

        # SMA
        df["SMA"] = df["Close"].rolling(self.config.sma_period).mean()

        # 回檔深度：每日 Close 相對 Donchian_High 的比率
        df["Pullback_Depth"] = (df["Close"] - df["Donchian_High"]) / df["Donchian_High"]

        # 最近 N 日內是否曾有足夠深度的回檔
        lookback = self.config.pullback_lookback
        threshold = -self.config.pullback_threshold
        df["Had_Pullback"] = df["Pullback_Depth"].rolling(lookback).min() <= threshold

        # SMA 斜率：SMA(50) 是否在上升
        slope_lb = self.config.sma_slope_lookback
        df["SMA_Rising"] = df["SMA"] > df["SMA"].shift(slope_lb)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：收盤價突破 Donchian 上軌
        cond_breakout = df["Close"] > df["Donchian_High"]

        # 條件二：收盤價 > SMA(50)
        cond_trend = df["Close"] > df["SMA"]

        # 條件三：近期曾有回檔
        cond_pullback = df["Had_Pullback"]

        # 條件四：SMA(50) 上升中（Att3: 過濾熊市假突破）
        cond_sma_rising = df["SMA_Rising"]

        df["Signal"] = cond_breakout & cond_trend & cond_pullback & cond_sma_rising

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
                "SIVR: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SIVR: Detected %d Donchian breakout signals", signal_count)
        return df

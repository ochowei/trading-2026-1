"""
SIVR-010 訊號偵測器：Trend Following (SMA Crossover + Pullback)
SIVR-010 Signal Detector: 趨勢跟蹤（SMA 金叉 + 回調進場）

Attempt 3: 不使用 GLD 參考標的，改用 SIVR 自身趨勢。

進場條件（全部滿足）：
1. SMA(20) > SMA(50)（金叉狀態）
2. 5日高點回撤 3-8%（趨勢中回調）
3. 收盤價 > SMA(50)（在上升趨勢之上）
4. SMA(20) 5日斜率 > 0（趨勢仍在加速/持平）
5. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_010_rs_momentum.config import SIVRRSMomentumConfig

logger = logging.getLogger(__name__)


class SIVRRSMomentumDetector(BaseSignalDetector):
    """SIVR 趨勢跟蹤訊號偵測器"""

    def __init__(self, config: SIVRRSMomentumConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA
        df["SMA_Fast"] = df["Close"].rolling(self.config.sma_fast_period).mean()
        df["SMA_Slow"] = df["Close"].rolling(self.config.sma_slow_period).mean()

        # SMA(20) 5日斜率（正值表示趨勢加速）
        df["SMA_Fast_Slope"] = df["SMA_Fast"] - df["SMA_Fast"].shift(5)

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA(20) > SMA(50) 金叉狀態
        cond_golden_cross = df["SMA_Fast"] > df["SMA_Slow"]

        # 短期回調在範圍內
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )

        # 收盤價在 SMA(50) 之上
        cond_above_sma = df["Close"] > df["SMA_Slow"]

        # SMA(20) 5日斜率 > 0
        cond_slope = df["SMA_Fast_Slope"] > 0

        df["Signal"] = cond_golden_cross & cond_pullback & cond_above_sma & cond_slope

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
            logger.info("SIVR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("SIVR: Detected %d trend following signals", signal_count)
        return df

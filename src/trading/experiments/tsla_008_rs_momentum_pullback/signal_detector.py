"""
TSLA-008 訊號偵測器：BB Squeeze Breakout + SMA Golden Cross
TSLA-008 Signal Detector: BB Squeeze with Golden Cross Trend Filter

進場條件（全部滿足）：
1. BB Width 在過去 60 日的 25th 百分位以下（近 5 日內曾發生）
2. 收盤價 > 上軌 Bollinger Band（突破確認）
3. SMA(20) > SMA(50)（金叉趨勢確認，比 Close>SMA(50) 更嚴格）
4. 冷卻期 15 個交易日

Att3 假說：SMA 金叉過濾 2022 熊市中 Close 暫時突破 SMA(50) 的假突破，
因為金叉需要短期均線持續在長期均線之上，而非只靠單日收盤。
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_008_rs_momentum_pullback.config import TSLA008Config

logger = logging.getLogger(__name__)


class TSLA008Detector(BaseSignalDetector):
    """TSLA-008 BB Squeeze + Golden Cross 訊號偵測器"""

    def __init__(self, config: TSLA008Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        period = self.config.bb_period
        std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(period).mean()
        df["BB_Std"] = df["Close"].rolling(period).std()
        df["BB_Upper"] = df["BB_Mid"] + std * df["BB_Std"]
        df["BB_Width"] = (2 * std * df["BB_Std"]) / df["BB_Mid"]

        # BB Width percentile (rolling)
        window = self.config.bb_squeeze_percentile_window
        pct = self.config.bb_squeeze_percentile
        df["BB_Width_Pctile"] = (
            df["BB_Width"]
            .rolling(window)
            .apply(lambda x: np.sum(x <= x.iloc[-1]) / len(x), raw=False)
        )

        # 近 N 日內是否有擠壓
        recent = self.config.bb_squeeze_recent_days
        df["BB_Squeeze_Recent"] = df["BB_Width_Pctile"].rolling(recent, min_periods=1).min().le(pct)

        # SMA Golden Cross
        df["SMA_Short"] = df["Close"].rolling(self.config.sma_short_period).mean()
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # BB 擠壓（近 5 日內）
        cond_squeeze = df["BB_Squeeze_Recent"]

        # 突破上軌
        cond_breakout = df["Close"] > df["BB_Upper"]

        # SMA 金叉趨勢確認
        cond_trend = df["SMA_Short"] > df["SMA_Long"]

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend

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

        signal_count = df["Signal"].sum()
        logger.info("TSLA: Detected %d BB squeeze golden cross signals", signal_count)
        return df

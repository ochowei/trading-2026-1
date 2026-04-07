"""
SPY-007 訊號偵測器：Momentum Pullback to SMA(20)
SPY-007 Signal Detector: Momentum Pullback to SMA(20)

進場條件（全部滿足）：
1. Close > SMA(200)（長期上升趨勢，排除熊市）
2. SMA(20) > SMA(50)（短期動能確認）
3. Low <= SMA(20)（回調至短期支撐）
4. Close > SMA(20)（反彈站回確認）
5. ClosePos >= 40%（日內反轉確認）
6. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.spy_007_trend_pullback.config import SPY007TrendPullbackConfig

logger = logging.getLogger(__name__)


class SPY007TrendPullbackDetector(BaseSignalDetector):
    """SPY Momentum Pullback 訊號偵測器"""

    def __init__(self, config: SPY007TrendPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["SMA_Short"] = df["Close"].rolling(self.config.sma_short_period).mean()
        df["SMA_Mid"] = df["Close"].rolling(self.config.sma_mid_period).mean()
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        # Close Position: 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Long-term uptrend: Close > SMA(200)
        cond_long_uptrend = df["Close"] > df["SMA_Long"]

        # 2. Short-term momentum: SMA(20) > SMA(50)
        cond_momentum = df["SMA_Short"] > df["SMA_Mid"]

        # 3. Pullback to SMA(20): Low dipped to or below SMA(20)
        cond_pullback = df["Low"] <= df["SMA_Short"]

        # 4. Bounce: Close above SMA(20)
        cond_bounce = df["Close"] > df["SMA_Short"]

        # 5. Close Position filter: day-end reversal confirmation
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = (
            cond_long_uptrend & cond_momentum & cond_pullback & cond_bounce & cond_reversal
        )

        # Cooldown
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
        logger.info("SPY-007: Detected %d momentum pullback signals", signal_count)
        return df

"""
FCX-008 訊號偵測器：Trend Pullback to SMA(50)
FCX-008 Signal Detector: Trend Pullback to SMA(50)

進場條件（全部滿足）：
1. SMA(50) > SMA(200)（黃金交叉，確認上升趨勢）
2. SMA(50) > SMA(50)[10日前]（SMA(50) 仍在上升，趨勢健康）
3. Low <= SMA(50) * 1.02（當日最低價回測至 SMA(50) 附近）
4. Close > SMA(50)（收盤反彈站回支撐上方）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_008_trend_pullback.config import FCXTrendPullbackConfig

logger = logging.getLogger(__name__)


class FCXTrendPullbackDetector(BaseSignalDetector):
    """FCX Trend Pullback 訊號偵測器"""

    def __init__(self, config: FCXTrendPullbackConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["SMA_Fast"] = df["Close"].rolling(self.config.sma_fast_period).mean()
        df["SMA_Slow"] = df["Close"].rolling(self.config.sma_slow_period).mean()

        # SMA(50) slope: compare current vs N days ago
        n = self.config.sma_slope_lookback
        df["SMA_Fast_Prev"] = df["SMA_Fast"].shift(n)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Golden cross: SMA(50) > SMA(200)
        cond_uptrend = df["SMA_Fast"] > df["SMA_Slow"]

        # 2. SMA(50) is rising
        cond_rising = df["SMA_Fast"] > df["SMA_Fast_Prev"]

        # 3. Pullback to SMA(50): Low dipped to within proximity
        proximity = self.config.proximity_pct
        cond_pullback = df["Low"] <= df["SMA_Fast"] * (1 + proximity)

        # 4. Bounce: Close above SMA(50)
        cond_bounce = df["Close"] > df["SMA_Fast"]

        df["Signal"] = cond_uptrend & cond_rising & cond_pullback & cond_bounce

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
        logger.info("FCX-008: Detected %d trend pullback signals", signal_count)
        return df

"""
FCX-007 訊號偵測器：Donchian Channel Breakout + BB Squeeze
FCX-007 Signal Detector: Donchian Breakout with Volatility Contraction

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Donchian(30) 上軌（30日最高價突破）
3. 收盤價 > SMA(50)（趨勢向上）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_007_donchian_breakout.config import FCXDonchianConfig

logger = logging.getLogger(__name__)


class FCXDonchianDetector(BaseSignalDetector):
    """FCX Donchian Channel Breakout 訊號偵測器"""

    def __init__(self, config: FCXDonchianConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian Channel upper band: highest high of past N days (excluding today)
        period = self.config.donchian_period
        df["Donchian_Upper"] = df["High"].shift(1).rolling(period).max()

        # Bollinger Bands for squeeze detection
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        bb_mid = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        bb_upper = bb_mid + bb_std * rolling_std
        bb_lower = bb_mid - bb_std * rolling_std
        df["BB_Width"] = (bb_upper - bb_lower) / bb_mid

        # BB Width percentile rank over window
        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        # Recent squeeze: was there a squeeze in the last N days?
        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Recent BB squeeze in past 5 days
        cond_squeeze = df["Recent_Squeeze"]

        # Breakout: close above Donchian upper (new 30-day high)
        cond_breakout = df["Close"] > df["Donchian_Upper"]

        # Uptrend: close above SMA(50)
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend

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
        logger.info("FCX: Detected %d Donchian squeeze breakout signals", signal_count)
        return df

"""
TSLA-013 訊號偵測器：BB 擠壓突破 + 突破前平靜度過濾
TSLA-013 Signal Detector: BB Squeeze Breakout + Pre-Breakout Calm Filter

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（波動收縮；同 TSLA-009 Att2）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（趨勢向上）
4. 訊號日前一日（T-1）報酬 ∈ [prev_day_return_min, prev_day_return_max]
5. Close / SMA(50) ≤ sma_extension_max（Att3 新增：排除已遠離 SMA 的延伸突破）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_013_pre_breakout_calm.config import (
    TSLAPreBreakoutCalmConfig,
)

logger = logging.getLogger(__name__)


class TSLAPreBreakoutCalmDetector(BaseSignalDetector):
    """TSLA BB Squeeze Breakout + Pre-Breakout Calm Filter 訊號偵測器"""

    def __init__(self, config: TSLAPreBreakoutCalmConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()
        df["Prev_Day_Return"] = df["Close"].pct_change().shift(1)
        df["SMA_Extension"] = df["Close"] / df["SMA_Trend"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]

        prev_ret = df["Prev_Day_Return"]
        cond_prev_day_calm = (prev_ret >= self.config.prev_day_return_min) & (
            prev_ret <= self.config.prev_day_return_max
        )
        cond_sma_not_extended = df["SMA_Extension"] <= self.config.sma_extension_max

        df["Signal"] = (
            cond_squeeze & cond_breakout & cond_trend & cond_prev_day_calm & cond_sma_not_extended
        )

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
        logger.info(
            "TSLA: Detected %d BB squeeze breakout + pre-breakout calm signals",
            signal_count,
        )
        return df

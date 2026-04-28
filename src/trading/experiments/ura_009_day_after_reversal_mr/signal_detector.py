"""
URA Day-After Capitulation Mean Reversion 訊號偵測器 (URA-009)

進場條件（全部針對進場日 T 計算；T-1 為昨日評估日）：
1. 昨日（T-1）收盤 vs 過去 10 日最高價回檔 ≥ 10%
2. 昨日（T-1）回檔 ≤ 20%（過濾極端崩盤）
3. 昨日（T-1）Williams %R(10) ≤ -85（極端超賣）
4. 兩日跌幅 Close[T-1] / Close[T-3] - 1 ≤ -4%
5. 今日（T）Close > 昨日（T-1）High（收盤收復昨日高點，Att2 強化過濾）
6. 今日（T）Close > 今日（T）Open（陽線 K 線）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_009_day_after_reversal_mr.config import (
    URADayAfterReversalMRConfig,
)

logger = logging.getLogger(__name__)


class URADayAfterReversalMRSignalDetector(BaseSignalDetector):
    """URA 日後資本化 + 單K反轉 訊號偵測器"""

    def __init__(self, config: URADayAfterReversalMRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 兩日跌幅：今日 close 相對兩日前 close
        df["TwoDayDecline"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # T-1 評估：pullback、WR、2DD 均取前一日值
        prev_pullback = df["Pullback"].shift(1)
        prev_wr = df["WR"].shift(1)
        prev_two_day_decline = df["TwoDayDecline"].shift(1)
        prev_high = df["High"].shift(1)

        cond_pullback_min = prev_pullback <= self.config.pullback_threshold
        cond_pullback_cap = prev_pullback >= self.config.pullback_upper
        cond_wr = prev_wr <= self.config.wr_threshold
        cond_decline = prev_two_day_decline <= self.config.two_day_decline

        # 今日反轉強度：Close > 昨日 High（收盤收復昨日高點）
        # 同時要求陽線 Close > Open（日內買盤壓過賣壓）
        cond_reclaim = df["Close"] > prev_high
        cond_bullish_bar = df["Close"] > df["Open"]

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_cap
            & cond_wr
            & cond_decline
            & cond_reclaim
            & cond_bullish_bar
        )

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
            logger.info("URA-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA-009: Detected %d Day-After Capitulation signals", signal_count)
        return df

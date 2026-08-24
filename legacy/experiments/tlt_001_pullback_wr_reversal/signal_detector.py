"""
TLT 回檔範圍 + Williams %R + 反轉K線訊號偵測器
(TLT Pullback Range + Williams %R + Reversal Candle Signal Detector)

進場條件（全部滿足）：
1. 10 日高點回檔 3-7%（過濾不足與極端回撤）
2. Williams %R(10) ≤ -80（超賣）
3. 收盤位置 ≥ 40%（日內反轉確認）
4. 冷卻期 7 個交易日

Entry conditions (all must be met):
1. Pullback 3-7% from 10-day high (range filter)
2. Williams %R(10) <= -80 (oversold)
3. Close position >= 40% (intraday reversal confirmation)
4. 7-day cooldown between signals
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_001_pullback_wr_reversal.config import (
    TLTPullbackWRReversalConfig,
)

logger = logging.getLogger(__name__)


class TLTPullbackWRReversalSignalDetector(BaseSignalDetector):
    def __init__(self, config: TLTPullbackWRReversalConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔範圍：pullback_upper <= Pullback <= pullback_threshold
        # (Pullback is negative, so upper bound is more negative)
        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback_min & cond_pullback_max & cond_wr & cond_reversal

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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
        logger.info("TLT: Detected %d Pullback Range+WR+Reversal signals", signal_count)
        return df

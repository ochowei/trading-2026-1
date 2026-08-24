"""
GLD-014 訊號偵測器：Signal-Day Capitulation-Strength Filter MR

核心創新：在 GLD-012 pullback + WR + ClosePos 框架上新增「2 日累計跌幅下限」
過濾器（lesson #19 family 跨資產移植）。

進場條件（全部滿足）：
1. 收盤價低於 20 日高點 ≥ 3%（同 GLD-012）
2. Williams %R(10) ≤ -80（同 GLD-012）
3. 收盤位置 ≥ 40%（同 GLD-012）
4. 2 日累計報酬 <= -0.5%（GLD-014 新增：要求訊號日具備 capitulation 強度）
5. 冷卻期 7 個交易日（同 GLD-012）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_014_capitulation_filter.config import GLD014Config

logger = logging.getLogger(__name__)


class GLD014SignalDetector(BaseSignalDetector):
    def __init__(self, config: GLD014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（20日回看）
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

        # 1 日累計報酬（GLD-014 Att2 新增）
        df["Return_1d"] = df["Close"].pct_change(1)
        # 2 日累計報酬（GLD-014 新增）
        df["Return_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        # 1d floor：1 日跌幅必須 ≤ floor（Att1 停用為 -0.99）
        cond_oneday_floor = df["Return_1d"] <= self.config.oneday_return_floor
        # 2d floor：2 日跌幅必須 ≤ floor（更深於下限）
        cond_twoday_floor = df["Return_2d"] <= self.config.twoday_return_floor

        df["Signal"] = (
            cond_pullback & cond_wr & cond_reversal & cond_oneday_floor & cond_twoday_floor
        )

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
            logger.info("GLD-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "GLD-014: Detected %d Signal-Day Capitulation-Strength Filter signals",
            signal_count,
        )
        return df

"""
FXI-004 訊號偵測器：2日急跌均值回歸

Att3 進場條件（全部滿足）：
1. 10 日高點回檔 >= 5%（深度過濾）
2. 10 日高點回檔 <= 12%（隔離極端崩盤）
3. Williams %R(10) <= -80（超賣確認）
4. 2 日累計跌幅 <= -2.0%（急跌過濾，確保賣壓加速）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_004_rsi5_2d_decline.config import FXI004Config

logger = logging.getLogger(__name__)


class FXI004SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI004Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R(10)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 2 日累計跌幅
        df["Return_1d"] = df["Close"].pct_change()
        df["Decline_2d"] = df["Return_1d"] + df["Return_1d"].shift(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_2d_threshold

        df["Signal"] = cond_pullback & cond_cap & cond_wr & cond_decline

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
            logger.info(
                "FXI-004: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-004: Detected %d WR+2d-decline signals", signal_count)
        return df

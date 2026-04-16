"""
INDA-003 Att3 訊號偵測器：20日回檔+2日急跌均值回歸

進場條件（全部滿足）：
1. 20 日高點回檔 >= 4% 且 <= 10%（深回檔+崩盤隔離）
2. 2 日累計跌幅 >= 1.5%（急性賣壓確認）
3. Williams %R(10) <= -80（超賣確認）
4. 收盤位置 >= 40%（日內反轉確認）
5. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_003_bb_squeeze_breakout.config import INDA003Config

logger = logging.getLogger(__name__)


class INDA003SignalDetector(BaseSignalDetector):
    def __init__(self, config: INDA003Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 20 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # 2 日累計跌幅
        d = self.config.decline_days
        df["Decline_2d"] = df["Close"].pct_change(d)

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_pullback & cond_cap & cond_decline & cond_wr & cond_reversal

        # Cooldown
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
        logger.info("INDA-003: Detected %d 20d-pullback+2d-decline signals", signal_count)
        return df

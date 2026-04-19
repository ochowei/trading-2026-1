"""
XBI-012 訊號偵測器：Capitulation + Acceleration Reversal

進場條件（全部滿足）：
1. 10 日 pullback ≥ 6%（輕度環境濾波）
2. 10 日 pullback ≤ 20%（過濾極端崩盤）
3. 3 日 ROC ≤ -4%（短期急跌觸發）
4. 當日 Close > 前日 Close（Up day）
5. ClosePos ≥ 50%（當日收於區間上半）
6. Williams %R(10) ≤ -80（標準超賣濾波）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_012_capitulation_accel.config import XBI012Config

logger = logging.getLogger(__name__)


class XBI012SignalDetector(BaseSignalDetector):
    """XBI Capitulation + Acceleration Reversal 訊號偵測器"""

    def __init__(self, config: XBI012Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日 pullback (Close vs rolling High)
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # 3 日 ROC (Close / Close[-3] - 1)
        roc_n = self.config.roc_lookback
        df["ROC3"] = df["Close"] / df["Close"].shift(roc_n) - 1

        # 當日 ClosePos（當日 Close 在當日 (H, L) 區間的相對位置）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # Up day 旗標
        df["UpDay"] = df["Close"] > df["Close"].shift(1)

        # Williams %R(10)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_roc = df["ROC3"] <= self.config.roc_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_position_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold

        if self.config.require_up_day:
            cond_up = df["UpDay"]
        else:
            cond_up = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback & cond_upper & cond_roc & cond_closepos & cond_up & cond_wr
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
            logger.info(
                "XBI-012: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-012: Detected %d Capitulation+Acceleration reversal signals",
            signal_count,
        )
        return df

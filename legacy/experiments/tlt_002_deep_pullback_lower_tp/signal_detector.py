"""
TLT 回檔 + WR + 反轉K線 + 中期跌幅過濾訊號偵測器
(TLT Pullback + WR + Reversal + Medium-term Drawdown Filter Signal Detector)

進場條件（全部滿足）：
1. 10 日高點回檔 3-7%（同 TLT-001）
2. Williams %R(10) <= -80（同 TLT-001）
3. 收盤位置 >= 40%（同 TLT-001）
4. 60 日跌幅 <= 10%（新增：過濾持續性熊市環境）
5. 冷卻期 7 個交易日（同 TLT-001）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_002_deep_pullback_lower_tp.config import (
    TLTDeepPullbackLowerTPConfig,
)

logger = logging.getLogger(__name__)


class TLTDeepPullbackLowerTPSignalDetector(BaseSignalDetector):
    def __init__(self, config: TLTDeepPullbackLowerTPConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（同 TLT-001）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R（同 TLT-001）
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置（同 TLT-001）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # 60 日跌幅：Close vs 60 日前 Close
        mt = self.config.medium_term_lookback
        df["Close_MT"] = df["Close"].shift(mt)
        df["MT_Return"] = (df["Close"] - df["Close_MT"]) / df["Close_MT"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 原始條件（同 TLT-001）
        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        # 新增：60 日跌幅不超過上限
        cond_mt = df["MT_Return"] >= self.config.medium_term_max_drawdown

        df["Signal"] = cond_pullback_min & cond_pullback_max & cond_wr & cond_reversal & cond_mt

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
        logger.info("TLT: Detected %d Pullback+WR+Reversal+DD signals", signal_count)
        return df

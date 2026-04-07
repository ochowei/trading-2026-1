"""
XLU-006 Att3 訊號偵測器：回檔 + WR + 反轉K線 + TLT 利率環境過濾

進場條件（全部滿足）：
1. 10日回檔 >= 3.5% 且 <= 7%（回檔範圍）
2. Williams %R(10) <= -80（超賣確認）
3. 收盤位置 >= 40%（日內反轉確認）
4. TLT 60日 ROC > -5%（排除快速升息期）
5. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_006_rsi2_wide_sl.config import XLU006Config

logger = logging.getLogger(__name__)


class XLURSI2WideSLSignalDetector(BaseSignalDetector):
    def __init__(self, config: XLU006Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

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

        # TLT ROC（由 strategy 合併至 df["TLT_Close"]）
        if "TLT_Close" in df.columns:
            df["TLT_ROC"] = (
                df["TLT_Close"] - df["TLT_Close"].shift(self.config.tlt_roc_period)
            ) / df["TLT_Close"].shift(self.config.tlt_roc_period)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        # TLT 利率環境過濾
        if "TLT_ROC" in df.columns:
            cond_tlt = df["TLT_ROC"] > self.config.tlt_roc_threshold
        else:
            cond_tlt = True

        df["Signal"] = cond_pullback & cond_cap & cond_wr & cond_reversal & cond_tlt

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
        logger.info("XLU-006: Detected %d pullback + WR + TLT filter signals", signal_count)
        return df

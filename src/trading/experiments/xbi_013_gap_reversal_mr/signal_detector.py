"""
XBI-013 訊號偵測器：Gap-Down Capitulation + Intraday Reversal MR
(XBI-013 Signal Detector: Gap-Down Capitulation + Intraday Reversal MR)

進場條件（五項同時成立）：
1. 隔夜開盤跳空 (Open - PrevClose) / PrevClose <= -1.0%（生技事件投降拋壓）
2. 日內收盤高於開盤 Close > Open（日內資金撿便宜反轉）
3. 10 日高點回檔 in [-5%, -15%]（回檔範圍過濾）
4. Williams %R(10) <= -80（超賣確認）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_013_gap_reversal_mr.config import XBI013Config

logger = logging.getLogger(__name__)


class XBI013SignalDetector(BaseSignalDetector):
    """XBI-013：Gap-Down Capitulation + Intraday Reversal 訊號偵測器"""

    def __init__(self, config: XBI013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 隔夜跳空（今日開盤 vs 昨日收盤）
        df["PrevClose"] = df["Close"].shift(1)
        df["Gap"] = (df["Open"] - df["PrevClose"]) / df["PrevClose"]

        # 10 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_gap = df["Gap"] <= self.config.gap_threshold
        cond_reversal = df["Close"] > df["Open"]
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = cond_gap & cond_reversal & cond_pullback & cond_upper & cond_wr

        # 冷卻機制
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap_days = len(df.loc[last_signal:idx]) - 1
                if gap_days <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("XBI-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("XBI-013: Detected %d gap-down reversal signals", signal_count)
        return df

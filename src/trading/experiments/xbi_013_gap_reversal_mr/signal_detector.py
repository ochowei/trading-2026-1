"""
XBI-013 訊號偵測器：Gap-Down Capitulation + Intraday Reversal MR
(XBI-013 Signal Detector: Gap-Down Capitulation + Intraday Reversal MR)

Att2 當前結論（gap 改為補充過濾）：
- XBI-005 主框架（pullback 8-20% + WR + ClosePos ≥ 35%）+ Gap ≤ -1.0%（補充品質）
  + Close > Open（日內反轉）

進場條件（六項同時成立）：
1. 10 日高點回檔 in [-8%, -20%]（XBI-005 基線）
2. Williams %R(10) <= -80（XBI-005 基線）
3. 收盤位置 >= 35%（XBI-005 基線：日內反轉強度）
4. 隔夜開盤跳空 (Open - PrevClose) / PrevClose <= -1.0%（Att2 新增補充過濾）
5. Close > Open（日內陽 K，雙重確認反轉）
6. 冷卻期 10 個交易日
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

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # XBI-005 基線三項
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_position_threshold

        # Att2 新增補充過濾
        cond_gap = df["Gap"] <= self.config.gap_threshold
        if self.config.require_up_bar:
            cond_up_bar = df["Close"] > df["Open"]
        else:
            cond_up_bar = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_closepos
            & cond_gap
            & cond_up_bar
        )

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
        logger.info("XBI-013: Detected %d gap-down + XBI-005 filtered signals", signal_count)
        return df

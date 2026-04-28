"""
XBI-014 訊號偵測器：Post-Capitulation Vol-Transition MR

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 8-20%（同 XBI-005）
2. Williams %R(10) <= -80
3. ClosePos >= 35%（日內反轉確認）
4. 2 日報酬 <= drop_2d_floor（XBI-014 核心新增；預設 -2.0%）
5. 冷卻期 10 個交易日

設計依據（cross-asset port）：
- VGK-008 Att2 / INDA-010 Att3 / EEM-014 Att2 / USO-013 / IBIT-009 Att1 皆驗證
  「2DD floor 加深」過濾 shallow-2DD slow-melt drift 訊號
- XBI 2.0% vol 落於該模板 vol 適用區間 [0.97%, 3.17%] 內
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_014_vol_transition_mr.config import XBI014Config

logger = logging.getLogger(__name__)


class XBI014SignalDetector(BaseSignalDetector):
    def __init__(self, config: XBI014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        df["Return_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_drop_floor = df["Return_2d"] <= self.config.drop_2d_floor

        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_reversal & cond_drop_floor

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
            logger.info("XBI-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-014: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

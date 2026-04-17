"""
XBI-010 訊號偵測器：BB 下軌 OR 回檔深度混合進場均值回歸

進場條件：
1. Trigger: Close <= BB(20, 2.0) 下軌 OR 10日高點回檔 <= -8%
2. 10 日高點回檔 >= -12%（崩盤隔離，共同過濾器）
3. Williams %R(10) <= -80（超賣確認）
4. 收盤位置 >= 35%（日內反轉確認）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_010_bb_lower_pullback_cap.config import XBI010Config

logger = logging.getLogger(__name__)


class XBI010SignalDetector(BaseSignalDetector):
    """
    XBI-010：BB 下軌 OR 回檔混合進場

    進場邏輯：
    Trigger (OR): Close <= BB(20, 2.0) 下軌 OR 10日回檔 <= -8%
    AND 10 日高點回檔 >= -12%（排除極端崩盤）
    AND Williams %R(10) <= -80
    AND ClosePos >= 35%
    """

    def __init__(self, config: XBI010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（崩盤隔離）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
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

        # OR-triggered entry: BB lower band touched OR deep pullback
        cond_bb = df["Close"] <= df["BB_lower"]
        cond_pb_entry = df["Pullback"] <= self.config.pullback_entry_threshold
        cond_trigger = cond_bb | cond_pb_entry

        # AND filters
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_trigger & cond_cap & cond_wr & cond_reversal

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
            logger.info("XBI-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("XBI-010: Detected %d BB lower + cap hybrid signals", signal_count)
        return df

"""
FXI-010 訊號偵測器：Gap-Down 作為近期 capitulation regime filter
(FXI-010 Signal Detector: Gap-Down as Recent Capitulation Regime Filter)

Att3 進場條件（六項同時成立）：
1. 近 5 日內至少 1 日 Gap <= -2.0%（近期曾發生 capitulation 事件）
2. 10 日高點回檔 [-12%, -5%]（FXI-005 框架：深回檔但隔離崩盤）
3. Williams %R(10) <= -80（超賣確認）
4. Close Position >= 40%（日內反轉確認）
5. ATR(5)/ATR(20) > 1.05（波動率擴張過濾慢磨下跌）
6. 冷卻期 10 個交易日

備註：Att1/Att2 使用 gap-down 作為 entry trigger 均失敗（見 config.py
迭代歷程）。Att3 改為 gap-down regime filter + FXI-005 entry。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_010_gap_reversal_mr.config import FXI010Config

logger = logging.getLogger(__name__)


class FXI010SignalDetector(BaseSignalDetector):
    """FXI-010：Gap-Down Regime-Filtered MR 訊號偵測器"""

    def __init__(self, config: FXI010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 隔夜跳空
        df["PrevClose"] = df["Close"].shift(1)
        df["Gap"] = (df["Open"] - df["PrevClose"]) / df["PrevClose"]

        # 近 N 日內是否發生過 gap-down 事件
        gap_event = df["Gap"] <= self.config.gap_threshold
        df["RecentGapDown"] = gap_event.rolling(self.config.gap_lookback).sum() > 0

        # 10 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R(10)
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # Close Position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range.where(day_range > 0, float("nan"))
        df["ClosePos"] = df["ClosePos"].fillna(0.5)

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if self.config.use_gap_as_entry_trigger:
            # Att1/Att2 mode: gap-down on entry day
            cond_gap = df["Gap"] <= self.config.gap_threshold
            cond_reversal = df["Close"] > df["Open"]
            if self.config.require_close_above_midpoint:
                midpoint = (df["High"] + df["Low"]) / 2
                cond_reversal = cond_reversal & (df["Close"] > midpoint)
            cond_pullback_lower = df["Pullback"] <= self.config.pullback_threshold
            cond_pullback_upper = df["Pullback"] >= self.config.pullback_cap
            cond_wr = df["WR"] <= self.config.wr_threshold
            df["Signal"] = (
                cond_gap & cond_reversal & cond_pullback_lower & cond_pullback_upper & cond_wr
            )
        else:
            # Att3 mode: gap-down as regime filter + FXI-005 entry
            cond_regime = df["RecentGapDown"].fillna(False)
            cond_pullback_lower = df["Pullback"] <= self.config.pullback_threshold
            cond_pullback_upper = df["Pullback"] >= self.config.pullback_cap
            cond_wr = df["WR"] <= self.config.wr_threshold
            cond_cp = df["ClosePos"] >= self.config.close_position_threshold
            cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold
            df["Signal"] = (
                cond_regime
                & cond_pullback_lower
                & cond_pullback_upper
                & cond_wr
                & cond_cp
                & cond_atr
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
            logger.info("FXI-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FXI-010: Detected %d regime-filtered signals", signal_count)
        return df

"""
CIBR-010 NR7 Volatility Contraction + Pullback MR 訊號偵測器

在 pullback 情境下偵測 NR7（Narrowest Range 7）波動率壓縮模式，
作為賣壓衰竭 + 均值回歸進場的觸發條件。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_010_nr7_pullback_mr.config import CIBR010Config

logger = logging.getLogger(__name__)


class CIBR010SignalDetector(BaseSignalDetector):
    """
    CIBR-010：NR7 Volatility Contraction + Pullback Mean Reversion

    進場條件（可選 ATR 過濾）：
    1. 10 日高點回檔 >= 4%
    2. Williams %R(10) <= -80
    3. NR7：今日 True Range 為近 7 日最小
    4. ClosePos >= 40%
    5. （可選）ATR(5)/ATR(20) > 1.15
    """

    def __init__(self, config: CIBR010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日高點回檔
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

        # True Range（用於 NR7 判定與 ATR 計算）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["TR"] = tr

        # NR7：今日 TR 為近 nr_window 日最小（含今日）
        nr_n = self.config.nr_window
        df["TR_min_N"] = df["TR"].rolling(nr_n).min()
        df["IsNR"] = df["TR"] <= df["TR_min_N"]

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio（選用）
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # N 日報酬（用於 2 日跌幅過濾）
        df["Decline_N"] = df["Close"].pct_change(self.config.decline_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_nr = df["IsNR"]
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold

        signal = cond_pullback & cond_wr & cond_nr & cond_closepos

        if self.config.use_atr_filter:
            cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold
            signal = signal & cond_atr

        if self.config.use_decline_filter:
            cond_decline = df["Decline_N"] <= self.config.decline_threshold
            signal = signal & cond_decline

        df["Signal"] = signal

        # Cooldown
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
            logger.info("CIBR-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR-010: Detected %d NR7 + Pullback signals", signal_count)
        return df

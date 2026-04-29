"""
CIBR-012 Post-Capitulation Vol-Transition 訊號偵測器

核心創新：將 CIBR-008 的「ATR(5)/ATR(20) > 1.15 單一條件」替換為
「近期 ATR 峰值 + 當前 ATR 收縮」雙條件，以區分「急跌中」vs「急跌後」。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_012_vol_transition_mr.config import CIBR012Config

logger = logging.getLogger(__name__)


class CIBR012SignalDetector(BaseSignalDetector):
    """
    CIBR-012：Post-Capitulation Vol-Transition 均值回歸

    六條件同時成立時觸發訊號：
    1. Close <= BB(20, 2.0) 下軌
    2. 10 日高點回檔 >= -12%（崩盤隔離）
    3. Williams %R(10) <= -80
    4. ClosePos >= 40%
    5. 今日 ATR(5)/ATR(20) > 1.15（保留 CIBR-008 signal-day panic 過濾）
    6. 2 日報酬 >= -3.5%（排除 in-crash acceleration 進場，Att3 核心創新）
    """

    def __init__(self, config: CIBR012Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

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

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio (vol-transition indicator)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # 2 日報酬（close-to-close）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr_today = df["ATR_ratio"] > self.config.atr_today_threshold
        cond_twoday_cap = df["TwoDayReturn"] >= self.config.twoday_return_cap

        df["Signal"] = (
            cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr_today & cond_twoday_cap
        )

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
            logger.info("CIBR-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR-012: Detected %d Post-Capitulation Settling signals", signal_count)
        return df

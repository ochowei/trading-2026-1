"""
CIBR-008 BB 下軌 + 回檔上限混合進場訊號偵測器

在 BB(20,2.0) 下軌觸及時買入，搭配 10日高點回檔上限過濾極端崩盤，
再加上 WR+ATR+ClosePos 三重品質過濾。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_008_bb_lower_pullback_cap.config import CIBR008Config

logger = logging.getLogger(__name__)


class CIBR008SignalDetector(BaseSignalDetector):
    """
    CIBR-008：BB 下軌 + 回檔上限混合進場

    五條件同時成立時觸發訊號：
    1. Close <= BB(20,2.0) 下軌
    2. 10日高點回檔 >= 回檔上限（pullback 不比 -8% 更深，隔離極端崩盤）
    3. Williams %R(10) <= -80
    4. ClosePos >= 40%
    5. ATR(5)/ATR(20) > 1.15
    """

    def __init__(self, config: CIBR008Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10日高點回檔（崩盤隔離）
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

        # ATR ratio
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

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr

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
            logger.info("CIBR-008: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR-008: Detected %d BB Lower + Pullback Cap signals", signal_count)
        return df

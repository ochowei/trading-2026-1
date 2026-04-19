"""
CIBR-009 Key Reversal Day 訊號偵測器

進場條件（全部同時成立）：
1. 回檔 context：10日高點回檔 ∈ [-12%, -3%]
2. 超賣：WR(10) ≤ -80
3. 前日收黑：Prev Close < Prev Open
4. Stop-run：Today Low < Prev Low（突破前日最低）
5. 反轉確認：Today Close > Prev Close（站回前日收盤）
6. 當日收紅：Today Close > Today Open
7. 日內反轉：ClosePos ≥ 40%
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_009_key_reversal_day_mr.config import CIBR009Config

logger = logging.getLogger(__name__)


class CIBR009SignalDetector(BaseSignalDetector):
    """CIBR Key Reversal Day 偵測器"""

    def __init__(self, config: CIBR009Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10日高點回檔
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

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # 前日 OHLC
        df["Prev_Close"] = df["Close"].shift(1)
        df["Prev_Open"] = df["Open"].shift(1)
        df["Prev_Low"] = df["Low"].shift(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold

        # Key Reversal 結構
        cond_prev_bear = df["Prev_Close"] < df["Prev_Open"]
        cond_stop_run = df["Low"] < df["Prev_Low"]
        cond_reclaim = df["Close"] > df["Prev_Close"]
        cond_bull_bar = df["Close"] > df["Open"]
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_cap
            & cond_wr
            & cond_prev_bear
            & cond_stop_run
            & cond_reclaim
            & cond_bull_bar
            & cond_closepos
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
            logger.info("CIBR-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR-009: Detected %d Key Reversal Day signals", signal_count)
        return df

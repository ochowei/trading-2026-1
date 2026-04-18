"""
FXI-006 訊號偵測器：急跌均值回歸

Att3 進場條件（全部滿足）：
1. 2 日累計跌幅 <= -3.0%（直接測量急性賣壓）
2. ATR(5)/ATR(20) > 1.05（波動率飆升過濾）
3. ClosePos >= 40%（日內反轉確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_006_bb_lower_mr.config import FXI006Config

logger = logging.getLogger(__name__)


class FXI006SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI006Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 2-day cumulative decline
        df["Return_1d"] = df["Close"].pct_change()
        df["Decline_2d"] = df["Close"].pct_change(2)

        # Close Position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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

        cond_decline = df["Decline_2d"] <= self.config.decline_2d_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        df["Signal"] = cond_decline & cond_vol & cond_reversal

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
            logger.info(
                "FXI-006: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-006: Detected %d acute decline MR signals", signal_count)
        return df

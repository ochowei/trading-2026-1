"""
SIVR-013 訊號偵測器：Bollinger Band 下軌 + ATR 波動率自適應均值回歸

進場條件（全部滿足）：
1. Close < BB(20, 2) 下軌（價格跌破 2 標準差）
2. Williams %R(10) <= -80（超賣確認）
3. ATR(5)/ATR(20) > 1.05（波動率飆升，過濾慢磨下跌）
4. 回檔上限 15%（過濾極端崩盤）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_013_bb_lower_mr.config import SIVR013Config

logger = logging.getLogger(__name__)


class SIVR013SignalDetector(BaseSignalDetector):
    """SIVR-013 BB 下軌均值回歸訊號偵測器"""

    def __init__(self, config: SIVR013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_MA"] = df["Close"].rolling(n).mean()
        df["BB_STD"] = df["Close"].rolling(n).std()
        df["BB_Lower"] = df["BB_MA"] - self.config.bb_std * df["BB_STD"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # ATR ratio: short-term vs long-term volatility
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

        # 回檔幅度（用於上限過濾）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：Close < BB 下軌
        cond_bb = df["Close"] < df["BB_Lower"]

        # 條件二：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件三：ATR 波動率飆升
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        # 條件四：回檔上限（過濾極端崩盤）
        cond_cap = df["Pullback"] >= self.config.pullback_cap

        # 四條件同時成立
        df["Signal"] = cond_bb & cond_wr & cond_vol & cond_cap

        # 冷卻機制
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
                "SIVR-013: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SIVR-013: Detected %d BB lower band+WR signals", signal_count)
        return df

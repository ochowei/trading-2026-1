"""
CIBR BB 下軌均值回歸訊號偵測器

在 BB(20,2.0) 下軌觸及時買入，搭配 WR+ATR+ClosePos 三重品質過濾。
不同於 BB Squeeze Breakout（買在上軌突破），本策略在下軌買入（均值回歸方向）。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_007_bb_lower_mr.config import CIBRBBLowerMRConfig

logger = logging.getLogger(__name__)


class CIBRBBLowerMRSignalDetector(BaseSignalDetector):
    """
    CIBR BB 下軌均值回歸訊號偵測器

    五條件同時成立時觸發訊號：
    1. Close <= BB(20,2.0) 下軌（價格觸及或跌破 BB 下軌）
    2. Williams %R(10) <= -80（超賣確認）
    3. ClosePos >= 40%（日內反轉確認）
    4. ATR(5)/ATR(20) > 1.15（波動率急升，排除慢磨下跌）
    """

    def __init__(self, config: CIBRBBLowerMRConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

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

        # 條件一：價格觸及或跌破 BB 下軌
        cond_bb = df["Close"] <= df["BB_lower"]

        # 條件二：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        # 條件三：收盤位置確認反轉
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold

        # 條件四：波動率急升
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        # 四條件同時成立
        df["Signal"] = cond_bb & cond_wr & cond_closepos & cond_atr

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
            logger.info("CIBR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR: Detected %d BB Lower Band MR signals", signal_count)
        return df

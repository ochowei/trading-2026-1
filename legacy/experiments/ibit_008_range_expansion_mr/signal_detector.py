"""
IBIT-008 訊號偵測器：單日 Range Expansion Climax + 日內反轉均值回歸
(IBIT-008 Signal Detector: Single-bar Range Expansion Climax + Intraday Reversal MR)

進場條件（五項同時成立）：
1. 今日 True Range / ATR(20) ≥ 2.0（單日 TR 爆發 climax）
2. Close Position ≥ 50%（收盤價高於當日中點，強日內反轉）
3. 10 日高點回檔 ≤ -6%（下跌 regime 過濾）
4. 10 日回檔 ≥ -20%（崩盤上限）
5. Williams %R(10) ≤ -70（超賣確認）
6. 冷卻期 10 個交易日

True Range 定義（標準 Wilder 定義）：
    TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ibit_008_range_expansion_mr.config import IBIT008Config

logger = logging.getLogger(__name__)


class IBIT008SignalDetector(BaseSignalDetector):
    """IBIT-008：單日 Range Expansion Climax + 強日內反轉 訊號偵測器"""

    def __init__(self, config: IBIT008Config):
        self.config = config

    @staticmethod
    def _compute_true_range(df: pd.DataFrame) -> pd.Series:
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # True Range 與 ATR(20)（用 shift(1) 確保 ATR 不含今日，避免 look-ahead bias）
        df["TR"] = self._compute_true_range(df)
        atr_n = self.config.atr_period
        df["ATR20_prior"] = df["TR"].shift(1).rolling(atr_n).mean()
        df["TR_Ratio"] = df["TR"] / df["ATR20_prior"]

        # Close Position：收盤價在當日 High-Low 區間的位置（0-1）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range.where(day_range > 0, float("nan"))
        df["ClosePos"] = df["ClosePos"].fillna(0.5)  # 零範圍日視為中性

        # 回檔深度：收盤價 vs 近 N 日最高價
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

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_tr = df["TR_Ratio"] >= self.config.tr_ratio_threshold
        cond_close_pos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = cond_tr & cond_close_pos & cond_pullback & cond_upper & cond_wr

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
            logger.info("IBIT-008: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("IBIT-008: Detected %d range-expansion climax signals", signal_count)
        return df

"""
CIBR-011 訊號偵測器：單日 Range Expansion Climax + 日內反轉均值回歸
(CIBR-011 Signal Detector: Single-bar Range Expansion Climax + Intraday Reversal MR)

進場條件（六項同時成立 — Att3 反向 ATR）：
1. 今日 True Range / ATR(20) ≥ 1.7（Att2 放寬保留）
2. Close Position ≥ 50%（收盤價高於當日中點，強日內反轉）
3. 10 日高點回檔 ≤ -3%（淺回檔以上）
4. 10 日回檔 ≥ -10%（Att3 恢復原始上限）
5. Williams %R(10) ≤ -70（超賣確認）
6. ATR(5)/ATR(20) ≤ 1.10（Att3 反向：平靜 ATR + 單日爆發 = 真 capitulation）
7. 冷卻期 8 個交易日

True Range 定義（標準 Wilder 定義）：
    TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)

ATR(20) 採用 shift(1)：避免 look-ahead bias，今日 TR 與前 20 日 TR 平均比較。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_011_range_expansion_mr.config import CIBR011Config

logger = logging.getLogger(__name__)


class CIBR011SignalDetector(BaseSignalDetector):
    """CIBR-011：單日 Range Expansion Climax + 強日內反轉 訊號偵測器"""

    def __init__(self, config: CIBR011Config):
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

        # ATR 波動率比率（Att2 新增：capitulation regime 過濾）
        df["ATR_fast"] = df["TR"].rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = df["TR"].rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_tr = df["TR_Ratio"] >= self.config.tr_ratio_threshold
        cond_close_pos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        # Att3 反向 ATR 過濾：平靜 ATR regime + 單日爆發為真 capitulation
        cond_atr = df["ATR_ratio"] <= self.config.atr_ratio_max

        df["Signal"] = cond_tr & cond_close_pos & cond_pullback & cond_upper & cond_wr & cond_atr

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
            logger.info("CIBR-011: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR-011: Detected %d range-expansion climax signals", signal_count)
        return df

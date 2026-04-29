"""
TLT Day-After Capitulation + 強反轉 K 線 訊號偵測器 (TLT-006)

進場條件（全部針對進場候選日 T 計算，T-1 為昨日評估日）：
1. 昨日（T-1）10 日高點回檔 ≥ 3%
2. 昨日（T-1）10 日高點回檔 ≤ 8%（過濾 Fed 衝擊日類型的極端崩跌）
3. 昨日（T-1）Williams %R(10) ≤ -85（極端超賣）
4. 昨日（T-1）兩日跌幅 Close[T-1]/Close[T-3]-1 ≤ -1.5%
5. 今日（T）Close > 昨日（T-1）High（強反轉：收盤收復昨日高點）
6. 今日（T）Close > 今日（T）Open（陽線 K 線）

訊號在 T 當日收盤觸發，由執行模型於 T+1 開盤進場。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_006_day_after_reversal_mr.config import TLT006Config

logger = logging.getLogger(__name__)


class TLT006SignalDetector(BaseSignalDetector):
    """TLT-006：Day-After Capitulation + 強反轉 K 線"""

    def __init__(self, config: TLT006Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 兩日跌幅：Close[T]/Close[T-2] - 1
        df["TwoDayDecline"] = df["Close"].pct_change(2)

        # 當日 Range（High - Low）與過去 N 日 range 平均（不含今日）
        df["Range"] = df["High"] - df["Low"]
        lookback = self.config.range_expansion_lookback
        df["RangeAvg"] = df["Range"].shift(1).rolling(lookback).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # T-1 評估：pullback / WR / 2DD 均取昨日值
        prev_pullback = df["Pullback"].shift(1)
        prev_wr = df["WR"].shift(1)
        prev_two_day_decline = df["TwoDayDecline"].shift(1)
        prev_high = df["High"].shift(1)

        cond_pullback_min = prev_pullback <= self.config.pullback_threshold
        cond_pullback_cap = prev_pullback >= self.config.pullback_upper
        cond_wr = prev_wr <= self.config.wr_threshold
        cond_decline = prev_two_day_decline <= self.config.two_day_decline

        # T 反轉強度：Close > 昨日 High（收復昨日高點）且陽線
        cond_reclaim = df["Close"] > prev_high
        cond_bullish_bar = df["Close"] > df["Open"]

        # 擴張反轉：Range[T] ≥ 過去平均 range × 倍率（真正的 V 型擴張）
        if self.config.require_range_expansion:
            cond_range_expansion = df["Range"] >= (
                df["RangeAvg"] * self.config.range_expansion_ratio
            )
        else:
            cond_range_expansion = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_cap
            & cond_wr
            & cond_decline
            & cond_reclaim
            & cond_bullish_bar
            & cond_range_expansion
        )

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
            logger.info("TLT-006: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-006: Detected %d Day-After Capitulation signals", signal_count)
        return df

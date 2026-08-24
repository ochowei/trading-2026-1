"""
INDA-011 訊號偵測器：Multi-Period Capitulation-Strength Filter MR

延伸 INDA-010 Att3 框架，加入「3 日累積跌幅 cap」過濾器（Att3 最終）。
Repo 首次將「3DD cap」作為主要 capitulation-strength 過濾器於任何資產。

進場條件（全部滿足）：
1. 10 日高點回檔 in [-7%, -3%]
2. Williams %R(10) <= -80
3. 收盤位置 >= 40%
4. ATR(5) / ATR(20) > 1.15
5. 2 日報酬 <= -2.0%（沿用 INDA-010 Att3，深度下限）
6. **3 日報酬 >= -3.0%（INDA-011 Att3 核心創新：多週期持續性上限 cap）**
7. 冷卻期 7 個交易日

三次迭代路徑：
- Att1：3DD floor <= -3.5%（require 3DD 至少深）— min -0.09（失敗，方向錯誤）
- Att2：3DD cap >= -3.5%（require 3DD 不太深）— min 0.46（成功但 A/B 破壞）
- Att3 ★：3DD cap >= -3.0%（更嚴 cap）— min(A,B)† 0.55（+83% 全域最優）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_011_multi_period_capitulation.config import (
    INDA011Config,
)

logger = logging.getLogger(__name__)


class INDA011SignalDetector(BaseSignalDetector):
    def __init__(self, config: INDA011Config):
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

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

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
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        df["Return_2d"] = df["Close"].pct_change(2)
        df["Return_3d"] = df["Close"].pct_change(3)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_2d_floor = df["Return_2d"] <= self.config.drop_2d_floor
        cond_3d_floor = df["Return_3d"] <= self.config.drop_3d_floor
        cond_3d_cap = df["Return_3d"] >= self.config.drop_3d_cap

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_2d_floor
            & cond_3d_floor
            & cond_3d_cap
        )

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
            logger.info("INDA-011: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "INDA-011: Detected %d Multi-Period Capitulation-Strength signals",
            signal_count,
        )
        return df

"""
COPX-010 訊號偵測器：Post-Capitulation Vol-Transition MR

基於 COPX-007 的 20日回檔 + WR + ATR 框架，新增「2 日累計報酬」過濾器以區分
「崩盤加速中」vs「急跌後穩定期」進場時機。

進場條件（全部滿足）：
1. 20 日高點回檔 in [-20%, -10%]
2. Williams %R(10) <= -80
3. ATR(5) / ATR(20) > 1.05
4. 2 日累計報酬在 [twoday_return_floor, twoday_return_cap] 區間內
   - Att1（CIBR-012 方向）: 2DD >= -5.5% 過濾崩盤加速訊號
   - Att2（EEM/INDA 方向）: 2DD <= -2.5% 要求真實 capitulation
5. 冷卻期 12 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_010_vol_transition_mr.config import COPX010Config

logger = logging.getLogger(__name__)


class COPX010SignalDetector(BaseSignalDetector):
    def __init__(self, config: COPX010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 20 日高點回檔
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
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        # 2 日累計報酬（close-to-close）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        # 1 日報酬（close-to-close）
        df["OneDayReturn"] = df["Close"].pct_change()

        # 收盤位置 (Close Position)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_cap = df["TwoDayReturn"] >= self.config.twoday_return_cap
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor

        # 「弱 capitulation」過濾：只在「1日跌幅 > X% AND 收盤位置 > Y」時跳過
        # 等價於：保留訊號 iff 1日跌幅 <= X%（panic momentum）OR 收盤位置 <= Y（盤中拋售）
        # COPX losers 中最弱的兩筆（2019-05-06 / 2025-03-31）皆為高 ClosePos + 淺 1DD
        # 此 OR 邏輯避免 1DD floor 在 Part B 過濾盤中拋售型贏家（如 2024-08-07 CP 0.02）
        cond_weak_cap = (df["OneDayReturn"] > self.config.oneday_return_floor) & (
            df["ClosePos"] > self.config.weak_cap_closepos_threshold
        )

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_vol
            & cond_twoday_cap
            & cond_twoday_floor
            & ~cond_weak_cap
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
            logger.info("COPX-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-010: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

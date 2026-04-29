"""
FCX-011 訊號偵測器：Post-Capitulation Vol-Transition MR

在 BB 下軌 + 回檔上限混合進場框架上，可選加入「2 日報酬 floor 或 cap」
過濾器（Att2/Att3）。跨資產測試高波動單一個股（FCX ~3% vol）是否突破
XBI-010 驗證之 1.75% vol 上限。

進場條件（全部滿足）：
1. Close <= BB(20, 2.0) 下軌
2. 10 日高點回檔 >= pullback_cap（例：-15%，崩盤隔離）
3. Williams %R(10) <= -80
4. ClosePos >= 40%（日內反彈確認）
5. ATR(5)/ATR(20) > 1.15（signal-day panic 確認）
6.（可選）2 日收盤報酬 floor/cap 過濾
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_011_vol_transition_mr.config import FCX011Config

logger = logging.getLogger(__name__)


class FCX011SignalDetector(BaseSignalDetector):
    def __init__(self, config: FCX011Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
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

        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        signal = cond_bb & cond_cap & cond_wr & cond_reversal & cond_vol

        if self.config.use_twoday_filter:
            if self.config.twoday_direction == "floor":
                cond_twoday = df["TwoDayReturn"] <= self.config.twoday_threshold
            elif self.config.twoday_direction == "cap":
                cond_twoday = df["TwoDayReturn"] >= self.config.twoday_threshold
            else:
                raise ValueError(f"Invalid twoday_direction: {self.config.twoday_direction}")
            signal = signal & cond_twoday

        df["Signal"] = signal

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
            logger.info("FCX-011: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "FCX-011: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

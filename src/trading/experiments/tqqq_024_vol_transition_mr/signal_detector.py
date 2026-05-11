"""TQQQ-024 訊號偵測器：Post-Capitulation Vol-Transition MR

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌
2. 10 日高點回檔 ∈ [pullback_cap, pullback_floor]（中度回檔，排除崩盤）
3. Williams %R(10) <= -85（深度超賣）
4. ClosePos >= 35%（收盤強反轉確認）
5. ATR(5)/ATR(20) > atr_ratio_threshold（vol-transition panic 確認）
6. 2 日累計報酬 <= twoday_return_floor（require true 2-day capitulation depth）
7. 冷卻期 5 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_024_vol_transition_mr.config import TQQQ024Config

logger = logging.getLogger(__name__)


class TQQQ024SignalDetector(BaseSignalDetector):
    def __init__(self, config: TQQQ024Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Bollinger Bands
        bb_mid = df["Close"].rolling(cfg.bb_period).mean()
        bb_std = df["Close"].rolling(cfg.bb_period).std()
        df["BB_lower"] = bb_mid - cfg.bb_std * bb_std

        # 10 日高點回檔
        high_n = df["High"].rolling(cfg.pullback_lookback).max()
        df["Pullback"] = (df["Close"] - high_n) / high_n

        # Williams %R
        highest = df["High"].rolling(cfg.wr_period).max()
        lowest = df["Low"].rolling(cfg.wr_period).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio（signal-day panic）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_short = tr.rolling(cfg.atr_short_period).mean()
        atr_long = tr.rolling(cfg.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        # 2 日累計報酬
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_pullback_floor = df["Pullback"] <= cfg.pullback_floor
        cond_pullback_cap = df["Pullback"] >= cfg.pullback_cap
        cond_wr = df["WR"] <= cfg.wr_threshold
        cond_reversal = df["ClosePos"] >= cfg.close_position_threshold
        cond_vol = df["ATR_Ratio"] > cfg.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= cfg.twoday_return_floor

        df["Signal"] = (
            cond_bb
            & cond_pullback_floor
            & cond_pullback_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
        )

        # 冷卻機制
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("TQQQ-024: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-024: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

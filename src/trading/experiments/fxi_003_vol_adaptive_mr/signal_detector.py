"""
FXI-003 訊號偵測器：波動率自適應均值回歸

進場條件（全部滿足）：
1. 10 日高點回檔 ≥ 7%（與 FXI-001 一致）
2. Williams %R(10) ≤ -80（超賣確認）
3. ATR(5)/ATR(20) > 1.10（波動率急升，恐慌急跌而非慢磨）
4. ClosePos ≥ 35%（日內反轉確認，收盤不在最低點）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_003_vol_adaptive_mr.config import FXI003Config

logger = logging.getLogger(__name__)


class FXI003SignalDetector(BaseSignalDetector):
    def __init__(self, config: FXI003Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Pullback from recent high
        rolling_high = df["High"].rolling(self.config.pullback_lookback).max()
        df["Pullback"] = (df["Close"] - rolling_high) / rolling_high

        # Williams %R
        rolling_high_wr = df["High"].rolling(self.config.wr_period).max()
        rolling_low_wr = df["Low"].rolling(self.config.wr_period).min()
        df["WR"] = (rolling_high_wr - df["Close"]) / (rolling_high_wr - rolling_low_wr) * -100

        # ATR ratio (fast / slow)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_Slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_Ratio"] = df["ATR_Fast"] / df["ATR_Slow"]

        # Close Position (close relative to day's range)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range.replace(0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_closepos = df["ClosePos"] >= self.config.closepos_threshold

        df["Signal"] = cond_pullback & cond_wr & cond_atr & cond_closepos

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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

        signal_count = df["Signal"].sum()
        logger.info("FXI-003: Detected %d vol-adaptive MR signals", signal_count)
        return df

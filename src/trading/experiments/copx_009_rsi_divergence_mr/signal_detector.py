"""
COPX-009 訊號偵測器：RSI Bullish Divergence + Pullback+WR+ATR 均值回歸

進場條件（全部滿足）：
1. 收盤價相對 20 日最高價回檔 10-20%
2. Williams %R(10) <= -80（超賣確認）
3. ATR(5) / ATR(20) > 1.05（波動率飆升）
4. RSI(14) bullish hook：RSI 自過去 5 日最低點回升 >= 3 點，且該最低點 <= 35
5. 冷卻期 12 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_009_rsi_divergence_mr.config import COPX009Config

logger = logging.getLogger(__name__)


class COPX009SignalDetector(BaseSignalDetector):
    """COPX-009 RSI Bullish Divergence + Pullback+WR+ATR 訊號偵測器"""

    def __init__(self, config: COPX009Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

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

        rsi_n = self.config.rsi_period
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.rolling(rsi_n).mean()
        avg_loss = loss.rolling(rsi_n).mean()
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        df["RSI"] = 100 - (100 / (1 + rs))

        hook_n = self.config.rsi_hook_lookback
        df["RSI_Min_N"] = df["RSI"].rolling(hook_n).min()
        df["RSI_Hook_Delta"] = df["RSI"] - df["RSI_Min_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
        cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min

        if self.config.enable_atr_filter:
            cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
            df["Signal"] = (
                cond_pullback
                & cond_upper
                & cond_wr
                & cond_vol
                & cond_hook_delta
                & cond_hook_oversold
            )
        else:
            df["Signal"] = (
                cond_pullback & cond_upper & cond_wr & cond_hook_delta & cond_hook_oversold
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
            logger.info(
                "COPX-009: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("COPX-009: Detected %d RSI-divergence pullback+WR+ATR signals", signal_count)
        return df

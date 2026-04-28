"""
XBI-011 訊號偵測器：RSI Bullish Divergence + Pullback+WR+ClosePos 均值回歸

進場條件（全部滿足）：
1. 收盤價相對 10 日最高價回檔 8-20%（同 XBI-005）
2. Williams %R(10) <= -80（超賣確認，同 XBI-005）
3. ClosePos >= 35%（日內反轉確認，同 XBI-005）
4. RSI(14) bullish hook：
   - RSI(14) 自過去 N 日最低點回升 ≥ H 點
   - 該最低點曾 ≤ 35（oversold 前提）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_011_rsi_divergence_mr.config import XBI011Config

logger = logging.getLogger(__name__)


class XBI011SignalDetector(BaseSignalDetector):
    """XBI RSI Bullish Divergence + Pullback+WR+ClosePos 訊號偵測器"""

    def __init__(self, config: XBI011Config):
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

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
        cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min

        df["Signal"] = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_reversal
            & cond_hook_delta
            & cond_hook_oversold
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
                "XBI-011: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-011: Detected %d RSI-Divergence Pullback+WR+ClosePos reversion signals",
            signal_count,
        )
        return df

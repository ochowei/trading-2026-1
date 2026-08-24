"""
FCX RSI Bullish Hook Divergence + Pullback+WR 訊號偵測器 (FCX-009)

四條件同時成立時觸發：
1. 10 日高點回檔 ≥ 9%（Pullback floor）
2. 10 日高點回檔 ≤ 18%（Pullback cap，過濾極端崩盤）
3. Williams %R(10) ≤ -80（超賣確認）
4. RSI(14) bullish hook：RSI 自過去 5 日最低點回升 ≥ 3 點，且最低點 ≤ 35
   （capitulation 尾聲訊號）

不使用 ClosePos 過濾（lesson #34：FCX 上反效果）。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_009_rsi_divergence_mr.config import (
    FCXRSIDivergenceMRConfig,
)

logger = logging.getLogger(__name__)


class FCXRSIDivergenceMRSignalDetector(BaseSignalDetector):
    """FCX RSI Bullish Hook Divergence + Pullback+WR 訊號偵測器"""

    def __init__(self, config: FCXRSIDivergenceMRConfig):
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

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
        cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min

        df["Signal"] = (
            cond_pullback_min & cond_pullback_cap & cond_wr & cond_hook_delta & cond_hook_oversold
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
            logger.info("FCX: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FCX: Detected %d RSI-Divergence Pullback+WR reversion signals", signal_count)
        return df

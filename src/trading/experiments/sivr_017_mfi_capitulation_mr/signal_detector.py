"""
SIVR-017 Money Flow Index Capitulation Mean Reversion 訊號偵測器

進場條件（同時成立）：
1. 收盤價相對 N 日最高價回檔 ≥ 7%（pullback floor）
2. 收盤價相對 N 日最高價回檔 ≤ 15%（pullback cap，過濾極端崩盤）
3. Williams %R(10) ≤ -80（短期超賣）
4. Money Flow Index(14) ≤ X（volume-weighted oversold）
5. （Att3 試驗）RSI(14) bullish hook 疊加：RSI 自過去 N 日最低點回升 ≥ H 點
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_017_mfi_capitulation_mr.config import SIVR017Config

logger = logging.getLogger(__name__)


class SIVRMFICapitulationMRSignalDetector(BaseSignalDetector):
    """SIVR-017：MFI volume-weighted capitulation 過濾於 SIVR-005 基礎進場"""

    def __init__(self, config: SIVR017Config):
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

        mfi_n = self.config.mfi_period
        typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
        raw_money_flow = typical * df["Volume"]
        tp_diff = typical.diff()
        positive_flow = raw_money_flow.where(tp_diff > 0, 0.0)
        negative_flow = raw_money_flow.where(tp_diff < 0, 0.0)
        pos_sum = positive_flow.rolling(mfi_n).sum()
        neg_sum = negative_flow.rolling(mfi_n).sum()
        money_ratio = pos_sum / neg_sum.replace(0, float("nan"))
        df["MFI"] = 100 - (100 / (1 + money_ratio))

        hook_mfi_n = self.config.mfi_hook_lookback
        df["MFI_Min_N"] = df["MFI"].rolling(hook_mfi_n).min()
        df["MFI_Hook_Delta"] = df["MFI"] - df["MFI_Min_N"]

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

        signal = cond_pullback_min & cond_pullback_cap & cond_wr

        if self.config.mfi_hook_enabled:
            cond_mfi_hook_delta = df["MFI_Hook_Delta"] >= self.config.mfi_hook_delta
            cond_mfi_hook_oversold = df["MFI_Min_N"] <= self.config.mfi_hook_max_min
            signal = signal & cond_mfi_hook_delta & cond_mfi_hook_oversold
        else:
            signal = signal & (df["MFI"] <= self.config.mfi_threshold)

        if self.config.rsi_hook_enabled:
            cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
            cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min
            signal = signal & cond_hook_delta & cond_hook_oversold

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
            logger.info("SIVR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("SIVR: Detected %d MFI Capitulation MR signals", signal_count)
        return df

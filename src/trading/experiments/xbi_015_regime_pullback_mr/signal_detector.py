"""
XBI-015 訊號偵測器：Multi-Week Regime-Aware Pullback Mean Reversion

進場條件（全部滿足）：
1. 收盤價相對 pullback_lookback 日最高價回檔在
   [pullback_upper, pullback_threshold]
2. Williams %R(wr_period) ≤ wr_threshold
3. ClosePos ≥ close_position_threshold（日內反轉確認）
4. （可選）ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （lesson #22 cross-strategy MR port：vol stability gate）
5. （可選）SMA(sma_regime_short) ≥ sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered trend regime，預設停用以避免 lesson #5 風險）
6. 冷卻 cooldown_days 個交易日

設計依據：lesson #22 buffered multi-week regime gate（TSLA-015 / NVDA-012 /
FCX-013 / COPX-011 BB Squeeze + NVDA-013 MBPC 五次跨資產驗證）首次跨**策略
類型**移植至 Pullback MR 框架，預期過濾「波動 transition expansion」期間的
假反彈訊號。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_015_regime_pullback_mr.config import XBI015Config

logger = logging.getLogger(__name__)


class XBI015RegimePullbackMRDetector(BaseSignalDetector):
    """XBI-015 訊號偵測器"""

    def __init__(self, config: XBI015Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === 回檔幅度（同 XBI-005）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 XBI-005）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # === ClosePos（同 XBI-005）===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === ATR regime（lesson #22 vol stability gate）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === SMA regime（lesson #22 trend regime，預設停用）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        if self.config.use_sma_regime:
            cond_regime_trend = df["SMA_Regime_Short"] >= (
                df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
            )
        else:
            cond_regime_trend = pd.Series(True, index=df.index)

        signal = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_reversal
            & cond_regime_vol
            & cond_regime_trend
        )

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
                "XBI-015: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-015: Detected %d regime-aware pullback MR signals",
            signal_count,
        )
        return df

"""
SOXL 優化出場訊號偵測模組 (SOXL Optimized Exit Signal Detector)
同 SOXL-005 進場邏輯，調整冷卻期。
三次嘗試均未能超越 SOXL-005。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_006_optimized_exit.config import SOXL006Config

logger = logging.getLogger(__name__)


class SOXL006SignalDetector(BaseSignalDetector):
    """
    SOXL 優化出場訊號偵測器

    條件同時成立時觸發訊號:
    1. 從 N 日高點回撤在 [cap, threshold] 範圍內（-40% ~ -25%）
    2. RSI(5) < 25
    3. 2 日累積跌幅 ≤ -8%
    """

    def __init__(self, config: SOXL006Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """計算 RSI (Wilder's smoothing)"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        df = df.copy()
        cfg = self.config
        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]
        df["RSI5"] = self._compute_rsi(df["Close"], cfg.rsi_period)
        df["Drop2D"] = df["Close"].pct_change(periods=2)
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號"""
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_cap = df["Drawdown"] >= cfg.drawdown_cap
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_drop2d = df["Drop2D"] <= cfg.drop_2d_threshold

        df["Signal"] = cond_drawdown & cond_cap & cond_rsi & cond_drop2d

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
            logger.info(f"[SOXL006Detector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號")

        signal_count = df["Signal"].sum()
        logger.info(f"[SOXL006Detector] SOXL: 偵測到 {signal_count} 個訊號")
        return df

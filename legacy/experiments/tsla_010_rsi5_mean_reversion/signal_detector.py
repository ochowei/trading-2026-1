"""
TSLA-010: RSI(5) Mean Reversion 訊號偵測器
TSLA RSI(5) Mean Reversion Signal Detector

改編 SOXL-006 框架：
1. 從 20 日高點回撤在 [-30%, -15%] 範圍內
2. RSI(5) < 20（vs TSLA-001 的 RSI(2) < 15，更穩定）
3. 2 日累積跌幅 ≤ -6%
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_010_rsi5_mean_reversion.config import (
    TSLARSI5MeanRevConfig,
)

logger = logging.getLogger(__name__)


class TSLARSI5MeanRevDetector(BaseSignalDetector):
    """TSLA RSI(5) 均值回歸訊號偵測器"""

    def __init__(self, config: TSLARSI5MeanRevConfig):
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
        """偵測 RSI(5) 均值回歸訊號"""
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
            logger.info(f"[TSLARSI5MeanRevDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號")

        signal_count = df["Signal"].sum()
        logger.info(f"[TSLARSI5MeanRevDetector] TSLA: 偵測到 {signal_count} 個 RSI(5) 均值回歸訊號")
        return df

"""
SOXL 深度超賣訊號偵測模組 (SOXL Deep Oversold Signal Detector)
與 SOXL-001 相同的三條件架構，但回撤門檻加深至 -25%。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_002_deep_oversold.config import SOXLDeepOversoldConfig

logger = logging.getLogger(__name__)


class SOXLDeepOversoldSignalDetector(BaseSignalDetector):
    """
    SOXL 深度超賣訊號偵測器

    三個條件同時成立時觸發訊號:
    1. 從 N 日高點回撤 ≥ threshold（-25%）
    2. RSI(5) < 25
    3. 成交量 > 1.5x 均量
    """

    def __init__(self, config: SOXLDeepOversoldConfig):
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
        df["Volume_SMA20"] = df["Volume"].rolling(window=cfg.volume_sma_period).mean()
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測深度超賣訊號"""
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]

        df["Signal"] = cond_drawdown & cond_rsi & cond_volume

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
            logger.info(f"[SOXLDeepOversoldDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號")

        signal_count = df["Signal"].sum()
        logger.info(f"[SOXLDeepOversoldDetector] SOXL: 偵測到 {signal_count} 個深度超賣訊號")
        return df

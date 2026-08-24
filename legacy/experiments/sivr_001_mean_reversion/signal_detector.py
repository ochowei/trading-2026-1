"""
SIVR 極端超賣均值回歸訊號偵測器 (SIVR Deep Oversold Mean Reversion Signal Detector)
雙條件同時成立時觸發訊號：RSI 超賣 + SMA 乖離。
Signal triggers when both conditions are met: RSI oversold + SMA deviation.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_001_mean_reversion.config import SIVRMeanReversionConfig

logger = logging.getLogger(__name__)


class SIVRSignalDetector(BaseSignalDetector):
    """
    SIVR 均值回歸訊號偵測器

    雙條件同時成立時觸發訊號：
    1. RSI(10) < 28 — 超賣
    2. SMA(20) 乖離 <= -2.5% — 價格顯著低於均線
    """

    def __init__(self, config: SIVRMeanReversionConfig):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # RSI
        df["RSI"] = self._compute_rsi(df["Close"], cfg.rsi_period)

        # SMA 與乖離
        df["SMA"] = df["Close"].rolling(window=cfg.sma_period).mean()
        df["SMA_Deviation"] = (df["Close"] - df["SMA"]) / df["SMA"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # 條件一：RSI 超賣
        cond_rsi = df["RSI"] < cfg.rsi_threshold

        # 條件二：SMA 乖離
        cond_sma_dev = df["SMA_Deviation"] <= cfg.sma_deviation_threshold

        # 雙條件同時成立
        df["Signal"] = cond_rsi & cond_sma_dev

        # 冷卻機制：N 個交易日內僅保留第一個訊號
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
            logger.info(
                f"[SIVRSignalDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號 "
                f"({len(suppressed)} duplicate signals suppressed by cooldown)"
            )

        signal_count = df["Signal"].sum()
        logger.info(
            f"[SIVRSignalDetector] SIVR: 偵測到 {signal_count} 個均值回歸訊號 "
            f"({signal_count} mean reversion signals detected)"
        )

        return df

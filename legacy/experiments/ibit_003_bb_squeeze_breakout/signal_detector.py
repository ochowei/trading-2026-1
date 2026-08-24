"""
IBIT-003 訊號偵測器：RSI(5) Trend Pullback (Attempt 3)
IBIT-003 Signal Detector: RSI(5) Trend Pullback

Att1（BB 擠壓突破）：Part A -0.29 / Part B -1.11
Att2（趨勢動量回檔）：Part A -0.07 / Part B 僅 1 訊號

Attempt 3 進場條件（全部滿足）：
1. 收盤價 > SMA(20)（短期上升趨勢確認）
2. RSI(5) < 25（短期超賣，SOXL 驗證有效的高波動振盪器）
3. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ibit_003_bb_squeeze_breakout.config import IBITRsi5TrendConfig

logger = logging.getLogger(__name__)


class IBITBBSqueezeDetector(BaseSignalDetector):
    """IBIT RSI(5) Trend Pullback 訊號偵測器"""

    def __init__(self, config: IBITRsi5TrendConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # RSI(5)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.rolling(self.config.rsi_period).mean()
        avg_loss = loss.rolling(self.config.rsi_period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100.0 - (100.0 / (1.0 + rs))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Short-term uptrend: close above SMA(20)
        cond_trend = df["Close"] > df["SMA_Trend"]

        # RSI(5) oversold
        cond_rsi = df["RSI"] < self.config.rsi_threshold

        df["Signal"] = cond_trend & cond_rsi

        # Cooldown mechanism
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

        signal_count = df["Signal"].sum()
        logger.info("IBIT: Detected %d RSI(5) trend pullback signals", signal_count)
        return df

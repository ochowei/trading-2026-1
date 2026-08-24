"""
COPX-006 訊號偵測器：RSI(2) 短期均值回歸
COPX-006 Signal Detector: RSI(2) Short-Term Mean Reversion

進場條件（全部滿足）：
1. RSI(2) < 15（極端短期超賣）
2. 2日跌幅 ≤ -3%（急跌確認）
3. 20日回檔 ≥ 5%（從近期高點回落）
4. 冷卻期 12 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_006_pairs_fcx.config import COPXRsi2Config

logger = logging.getLogger(__name__)


class COPXRsi2Detector(BaseSignalDetector):
    """COPX RSI(2) 短期均值回歸訊號偵測器"""

    def __init__(self, config: COPXRsi2Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2日跌幅
        df["Two_Day_Return"] = df["Close"].pct_change(2)

        # 20日回檔（從近期高點）
        lookback = self.config.pullback_lookback
        df["High_Nd"] = df["High"].rolling(lookback).max()
        df["Pullback"] = (df["Close"] - df["High_Nd"]) / df["High_Nd"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2) 極端超賣
        cond_rsi = df["RSI2"] < self.config.rsi_threshold

        # 2日急跌
        cond_decline = df["Two_Day_Return"] <= self.config.two_day_decline_threshold

        # 20日回檔達標
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        df["Signal"] = cond_rsi & cond_decline & cond_pullback

        # 冷卻機制
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
        logger.info("COPX: Detected %d RSI(2) mean reversion signals", signal_count)
        return df

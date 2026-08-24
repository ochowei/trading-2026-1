"""
COPX-008 Att3 訊號偵測器：Donchian Channel Breakout

進場條件（全部滿足）：
1. Close > 20日最高價（Donchian 上通道突破）
2. Close > SMA(50)（上升趨勢確認）
3. 冷卻期 12 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_008_rs_momentum.config import COPX008Config

logger = logging.getLogger(__name__)


class COPX008SignalDetector(BaseSignalDetector):
    """COPX Donchian 突破訊號偵測器"""

    def __init__(self, config: COPX008Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        # Donchian upper channel: highest high of past N days (excluding today)
        df["Donchian_High"] = df["High"].shift(1).rolling(cfg.donchian_period).max()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Close breaks above Donchian upper channel
        cond_breakout = df["Close"] > df["Donchian_High"]

        # Uptrend confirmation
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_breakout & cond_trend

        # Cooldown mechanism
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

        signal_count = df["Signal"].sum()
        logger.info("COPX-008: Detected %d Donchian breakout signals", signal_count)
        return df

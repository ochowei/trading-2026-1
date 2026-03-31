"""
SOXL-008 訊號偵測器：Williams %R(10) 振盪器測試
SOXL-008 Signal Detector: Williams %R(10) Oscillator Test

進場條件（全部滿足）：
1. 從 20 日高點回撤在 [-40%, -25%] 範圍內
2. Williams %R(10) ≤ -80（超賣確認）
3. 2 日累積跌幅 ≤ -8%（近期急跌確認）
4. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_008_wr_oscillator.config import (
    SOXLWROscillatorConfig,
)

logger = logging.getLogger(__name__)


class SOXLWROscillatorSignalDetector(BaseSignalDetector):
    """SOXL Williams %R 振盪器訊號偵測器"""

    def __init__(self, config: SOXLWROscillatorConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        df = df.copy()
        cfg = self.config

        # 20 日高點回撤
        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]

        # Williams %R
        high_n = df["High"].rolling(window=cfg.wr_period).max()
        low_n = df["Low"].rolling(window=cfg.wr_period).min()
        hl_range = high_n - low_n
        df["WR"] = ((high_n - df["Close"]) / hl_range) * -100.0
        df.loc[hl_range == 0, "WR"] = -50.0

        # 2 日累積跌幅
        df["Drop2D"] = df["Close"].pct_change(periods=2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測訊號"""
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_cap = df["Drawdown"] >= cfg.drawdown_cap
        cond_wr = df["WR"] <= cfg.wr_threshold
        cond_drop2d = df["Drop2D"] <= cfg.drop_2d_threshold

        df["Signal"] = cond_drawdown & cond_cap & cond_wr & cond_drop2d

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

        signal_count = df["Signal"].sum()
        logger.info("SOXL-008: Detected %d WR oscillator signals", signal_count)
        return df

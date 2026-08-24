"""TQQQ-029 TQQQ Donchian Channel Trend-Following 訊號偵測器

進場條件（T 日為訊號日，T+1 開盤進場）：
  1. Close > 前 donchian_period 日 High 之 rolling max（N 日新高 = 趨勢延續）
  2. Close > SMA(trend_sma_period)（中期趨勢向上確認）
  3. （可選 Att3）Close > SMA(bull_sma_period)（長期 bull regime）
  4. 冷卻期 cooldown_days 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_029_donchian_trend.config import TQQQ029Config

logger = logging.getLogger(__name__)


class TQQQ029SignalDetector(BaseSignalDetector):
    """TQQQ-029：Donchian N 日高點突破 + 趨勢確認（趨勢跟蹤）"""

    def __init__(self, config: TQQQ029Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Donchian 上軌：前 N 日（不含當日）High 之 rolling max
        df["Donchian_High"] = df["High"].rolling(cfg.donchian_period).max().shift(1)
        df["Trend_SMA"] = df["Close"].rolling(cfg.trend_sma_period).mean()
        df["Bull_SMA"] = df["Close"].rolling(cfg.bull_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_breakout = df["Close"] > df["Donchian_High"]
        cond_trend = df["Close"] > df["Trend_SMA"]

        if cfg.use_bull_filter:
            cond_bull = df["Close"] > df["Bull_SMA"]
        else:
            cond_bull = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_breakout.fillna(False) & cond_trend.fillna(False) & cond_bull.fillna(False)
        )

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
            logger.info(
                "TQQQ-029: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-029: Detected %d Donchian-trend signals "
            "(Donchian %dd high + SMA%d trend, bull filter=%s)",
            signal_count,
            cfg.donchian_period,
            cfg.trend_sma_period,
            cfg.use_bull_filter,
        )
        return df

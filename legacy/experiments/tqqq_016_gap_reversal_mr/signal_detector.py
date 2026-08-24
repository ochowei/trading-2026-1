"""
TQQQ-016 訊號偵測器：Gap-Down 資本化 + 日內反轉均值回歸
(TQQQ-016 Signal Detector: Gap-Down Capitulation + Intraday Reversal MR)

進場條件（Att3 最終版，5 + 1 項同時成立）：
1. 從 20 日高點回撤 <= -15%（深回撤均值回歸條件）
2. RSI(5) < 25（極端超賣確認）
3. 隔夜跳空 (Open - PrevClose) / PrevClose <= -2%（投降式盤外拋壓）
4. 日內收盤高於開盤 Close > Open（盤中資金撿便宜反轉）
5. Volume > 1.5x SMA(20)（真實拋壓確認）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_016_gap_reversal_mr.config import TQQQ016Config

logger = logging.getLogger(__name__)


class TQQQ016SignalDetector(BaseSignalDetector):
    """TQQQ-016：Gap-Down 資本化 + 日內反轉 訊號偵測器"""

    def __init__(self, config: TQQQ016Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder RSI（EMA 平滑，與大多數交易平台一致）"""
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

        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]
        df["RSI5"] = self._compute_rsi(df["Close"], cfg.rsi_period)

        df["PrevClose"] = df["Close"].shift(1)
        df["Gap"] = (df["Open"] - df["PrevClose"]) / df["PrevClose"]

        df["Volume_SMA20"] = df["Volume"].rolling(window=cfg.volume_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_gap = df["Gap"] <= cfg.gap_threshold
        cond_reversal = df["Close"] > df["Open"]
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]

        df["Signal"] = cond_drawdown & cond_rsi & cond_gap & cond_reversal & cond_volume

        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap_days = len(df.loc[last_signal:idx]) - 1
                if gap_days <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("TQQQ-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TQQQ-016: Detected %d gap-down reversal signals", signal_count)
        return df

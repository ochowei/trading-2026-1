"""
SOXL-013 訊號偵測器：Signal-Day Capitulation-Strength CAP MR

核心創新：在 SOXL-006 capitulation MR 框架（回撤 [-40%,-25%] + RSI(5)<20
+ 2DD≤-8%）上新增「3 日報酬 CAP」單維過濾器（lesson #19 family 跨資產移植，
方向經 trade-level 預分析由 1d-floor 校正為 3d-cap）。

進場條件（全部滿足）：
1. 從 20 日高點回撤在 [-40%, -25%]（同 SOXL-006）
2. RSI(5) < 20（同 SOXL-006；lesson #27 SOXL 不可用 RSI(2)）
3. 2 日累計跌幅 ≤ -8%（同 SOXL-006）
4. 3 日累計報酬 >= cap（SOXL-013 新維度：排除 regime-shift 級別深跌）
5. 冷卻期 7 個交易日（同 SOXL-006）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_013_signal_day_capitulation_cap.config import SOXL013Config

logger = logging.getLogger(__name__)


class SOXL013SignalDetector(BaseSignalDetector):
    """SOXL-013 Signal-Day Capitulation-Strength CAP 訊號偵測器"""

    def __init__(self, config: SOXL013Config):
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
        df["Return_3d"] = df["Close"].pct_change(periods=3)
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測 capitulation + 3d cap 訊號"""
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_cap = df["Drawdown"] >= cfg.drawdown_cap
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_drop2d = df["Drop2D"] <= cfg.drop_2d_threshold
        # 3 日 CAP：訊號日 3 日累計報酬必須 >= cap（排除 regime-shift 深跌）
        cond_3d_cap = df["Return_3d"] >= cfg.threeday_return_cap

        df["Signal"] = cond_drawdown & cond_cap & cond_rsi & cond_drop2d & cond_3d_cap

        # 冷卻機制（同 SOXL-006）
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
            logger.info("SOXL-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "SOXL-013: Detected %d Signal-Day Capitulation-Strength CAP signals",
            signal_count,
        )
        return df

"""SOXL-012 Volatility-Regime-Gated Capitulation Buy 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤在 [-40%, -25%] 範圍內（同 SOXL-006）
  2. RSI(5) < 20（同 SOXL-006）
  3. 2 日累積跌幅 ≤ -8%（同 SOXL-006）
  4. **BB(20, 2) 通道寬度 / Close < max_bb_width_ratio**（新增波動率 regime 閘門）
  5.（可選 Att3）T-N 日 Drawdown <= prior_drawdown_threshold（first-day-of-decline 過濾）
  6. 冷卻期 7 天（同 SOXL-006）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_006_selective_oversold.signal_detector import (
    SOXLSelectiveOversoldSignalDetector,
)
from trading.experiments.soxl_012_regime_vol_gate.config import SOXL012Config

logger = logging.getLogger(__name__)


class SOXL012SignalDetector(BaseSignalDetector):
    """SOXL-012：精選超賣 + 波動率 regime 閘門"""

    def __init__(self, config: SOXL012Config):
        self.config = config
        self._base_detector = SOXLSelectiveOversoldSignalDetector(config)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._base_detector.compute_indicators(df)

        cfg = self.config
        sma = df["Close"].rolling(cfg.bb_period).mean()
        std = df["Close"].rolling(cfg.bb_period).std()
        df["BB_Upper"] = sma + cfg.bb_std * std
        df["BB_Lower"] = sma - cfg.bb_std * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        df["Drawdown_Prior"] = df["Drawdown"].shift(cfg.prior_drawdown_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_cap = df["Drawdown"] >= cfg.drawdown_cap
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_drop2d = df["Drop2D"] <= cfg.drop_2d_threshold
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio

        signal = cond_drawdown & cond_cap & cond_rsi & cond_drop2d & cond_regime

        if cfg.enable_prior_drawdown_filter:
            cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold
            signal = signal & cond_prior_dd

        df["Signal"] = signal

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
                "SOXL-012: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "SOXL-012: Detected %d regime-gated capitulation signals",
            signal_count,
        )
        return df

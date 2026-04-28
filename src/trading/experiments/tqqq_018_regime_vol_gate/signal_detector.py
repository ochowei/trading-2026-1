"""TQQQ-018 Volatility-Regime-Gated Capitulation Buy 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-001 / TQQQ-010）
  2. RSI(5) < 25（同 TQQQ-001 / TQQQ-010）
  3. 成交量 > 1.5 × 20 日成交量均線（同 TQQQ-001 / TQQQ-010）
  4. **BB(20, 2) 通道寬度 / Close < max_bb_width_ratio**（新增波動率 regime 閘門）
  5. 冷卻期 3 天（同 TQQQ-001 / TQQQ-010）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config

logger = logging.getLogger(__name__)


class TQQQ018SignalDetector(BaseSignalDetector):
    """TQQQ-018：恐慌抄底 + 波動率 regime 閘門"""

    def __init__(self, config: TQQQ018Config):
        self.config = config
        self._base_detector = TQQQSignalDetector(config)

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
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        df["Signal"] = (
            cond_drawdown & cond_rsi & cond_volume & cond_regime & cond_prior_dd
        )

        # 冷卻機制（同 TQQQ-001）
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
                "TQQQ-018: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-018: Detected %d regime-gated capitulation signals",
            signal_count,
        )
        return df

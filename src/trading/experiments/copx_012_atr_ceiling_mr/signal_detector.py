"""
COPX-012 訊號偵測器：Volatility-Acceleration-Bounded Mean Reversion

進場條件（全部滿足）：
1. 收盤價相對 20 日最高價回檔 10-20%（同 COPX-007）
2. Williams %R(10) <= -80（超賣確認，同 COPX-007）
3. ATR(5)/ATR(20) **BAND ∈ (FLOOR, CEILING]**（lesson #15 v2 雙向）
   - FLOOR > 1.05（同 COPX-007，過濾 slow-grind）
   - CEILING <= 1.40（CIBR-014 / FXI-014 cross-asset，過濾 in-crash acceleration）
4. 冷卻期 12 個交易日

設計依據：
- lesson #15 v1（2026-Q1）：ATR(5)/ATR(20) > 1.15 separates panic from slow-grind
- lesson #15 v2（CIBR-014 Att2 / FXI-014 Att2 發現）：ATR ratio > X 標誌 in-crash
  acceleration phase，FLOOR + CEILING 形成 BAND 對稱失敗模式
- 跨資產證據：CIBR (1.53% vol) CEILING 1.40，FXI (2.0% vol) CEILING 1.35，
  推測 COPX (2.25% vol) CEILING 在 1.30-1.40 區間，需實驗確認
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_012_atr_ceiling_mr.config import COPX012Config

logger = logging.getLogger(__name__)


class COPX012SignalDetector(BaseSignalDetector):
    """COPX-012 Volatility-Acceleration-Bounded MR 訊號偵測器"""

    def __init__(self, config: COPX012Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        # N 日累計報酬（URA-013 dimension）
        n_window = self.config.return_cap_window
        df["Return_N"] = df["Close"].pct_change(n_window)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_vol_floor = df["ATR_Ratio"] > self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling
        cond_return_cap = df["Return_N"] >= self.config.return_cap_threshold

        df["Signal"] = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_vol_floor
            & cond_vol_ceiling
            & cond_return_cap
        )

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
            logger.info(
                "COPX-012: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-012: Detected %d ATR-band-bounded MR signals (FLOOR>%s, CEILING<=%s)",
            signal_count,
            self.config.atr_ratio_floor,
            self.config.atr_ratio_ceiling,
        )
        return df

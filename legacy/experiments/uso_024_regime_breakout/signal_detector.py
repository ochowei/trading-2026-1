"""
USO-024 訊號偵測器：Multi-Week Regime-Aware BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. **regime BOX**：k_min ≤ SMA(20) / SMA(60) ≤ k_max
   - k_min（lesson #22 標準下限，過濾 transition zone）
   - k_max（COPX-011 商品 ETF 新發現，過濾過熱牛末，預設 999=停用）
5. 冷卻期 10 個交易日

設計依據：lesson #22 + COPX-011 跨資產移植
- 商品 ETF（USO 原油 / COPX 銅礦）的過熱訊號可被 SMA20/SMA60 ratio 捕捉
- USO 23 次實驗均在 MR 框架，首次嘗試 regime-level 趨勢過濾
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_024_regime_breakout.config import USO024Config

logger = logging.getLogger(__name__)


class USO024RegimeBreakoutDetector(BaseSignalDetector):
    """USO-024 訊號偵測器"""

    def __init__(self, config: USO024Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        regime_ratio = df["SMA_Regime_Short"] / df["SMA_Regime_Long"]
        cond_regime_floor = regime_ratio >= self.config.sma_regime_ratio_min
        cond_regime_cap = regime_ratio <= self.config.sma_regime_ratio_max

        df["Signal"] = (
            cond_squeeze & cond_breakout & cond_trend & cond_regime_floor & cond_regime_cap
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

        signal_count = df["Signal"].sum()
        logger.info("USO-024: Detected %d regime-aware breakout signals", signal_count)
        return df

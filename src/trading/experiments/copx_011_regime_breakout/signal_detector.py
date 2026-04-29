"""
COPX-011 訊號偵測器：Multi-Week Regime-Aware BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. **regime BOX**：k_min ≤ SMA(20) / SMA(60) ≤ k_max
   - k_min=1.00（lesson #22 下限，FCX-013 標準，過濾 transition zone）
   - k_max=1.09（COPX-011 新發現，過濾過熱牛末，如 2024-05-14 SL ratio 1.094）
5. 冷卻期 12 個交易日

設計依據：lesson #22（TSLA-015 / NVDA-012 / FCX-013 跨資產驗證）+ COPX 新發現
- FCX 個股：純下限 k=1.00 即足（Part B SL 集中於 ratio<1.00）
- COPX ETF：需 BOX 結構（Part B SL 集中於 ratio>1.09 過熱牛末）
- 推測機制：ETF 平均化效應使 SMA20/SMA60 ratio 變化更平滑，過熱訊號在 ETF
  上更明顯（個股波動使 ratio 噪音更大，過熱信號被自然消除）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_011_regime_breakout.config import COPX011Config

logger = logging.getLogger(__name__)


class COPX011RegimeBreakoutDetector(BaseSignalDetector):
    """COPX-011 訊號偵測器"""

    def __init__(self, config: COPX011Config):
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
        logger.info("COPX-011: Detected %d regime-aware breakout signals", signal_count)
        return df

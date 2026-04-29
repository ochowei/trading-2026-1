"""
FCX-013 訊號偵測器：Multi-Week Regime-Aware BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. SMA(20) ≥ k × SMA(60)（多週期趨勢 regime，lesson #22 buffered）
5. 冷卻期 10 個交易日

設計依據：lesson #22（TSLA-015 / NVDA-012 跨資產驗證）
- 嚴格 SMA20>SMA60（k=1.00）會誤殺 transition winners 並觸發 cooldown chain
  shift（TSLA-015 Att1 案例）
- k=0.99（TSLA 1% 緩衝）/ k=0.97（NVDA 3% 緩衝）為各自甜蜜點
- FCX 為商品/礦業單股（~3% vol），需實測決定 k
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_013_regime_breakout.config import FCX013Config

logger = logging.getLogger(__name__)


class FCX013RegimeBreakoutDetector(BaseSignalDetector):
    """FCX-013 訊號偵測器"""

    def __init__(self, config: FCX013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Bollinger Bands ===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # BB Width 是否低於百分位門檻
        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        # 過去 N 日內是否曾擠壓
        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 FCX-004）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（lesson #22）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend & cond_regime_trend

        # 冷卻期
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
        logger.info("FCX-013: Detected %d regime-aware breakout signals", signal_count)
        return df

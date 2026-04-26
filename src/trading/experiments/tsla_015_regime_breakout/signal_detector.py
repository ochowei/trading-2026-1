"""
TSLA-015 訊號偵測器：Multi-Week Regime-Aware BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（趨勢向上）
4. SMA(20) > SMA(60)（多週期趨勢 regime 確認）
5. ATR(20) ≤ ATR(60) * vol_regime_max_ratio（多週期波動 regime 過濾）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_015_regime_breakout.config import TSLA015Config

logger = logging.getLogger(__name__)


class TSLA015RegimeBreakoutDetector(BaseSignalDetector):
    """TSLA-015 訊號偵測器"""

    def __init__(self, config: TSLA015Config):
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

        # === SMA 趨勢確認（同 TSLA-009）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === 多週期波動 regime（ATR 使用 Wilder's smoothing 等價的 EMA）===
        # True Range
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        cond_regime_vol = df["ATR_Regime_Short"] <= (
            df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
        )

        df["Signal"] = (
            cond_squeeze & cond_breakout & cond_trend & cond_regime_trend & cond_regime_vol
        )

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
        logger.info("TSLA-015: Detected %d regime-aware breakout signals", signal_count)
        return df

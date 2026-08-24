"""
NVDA-017 訊號偵測器：Signal-Day 5d Return CEILING on Multi-Week Regime-Aware MBPC

進場條件（全部滿足，沿用 NVDA-013 Att3 + 新增 5d return CEILING）：
1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
2. Close > SMA(sma_trend_period)
3. SMA(sma_regime_short) >= sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered multi-week SMA regime gate）
4. 5 日高點回檔 ∈ [pullback_max, pullback_min]
5. RSI(rsi_period) ∈ [rsi_min, rsi_max]
6. Close > Open（多頭 K 棒確認）
7. ATR(short) <= vol_regime_max_ratio × ATR(long)（vol regime gate）
8. **訊號日 5 日報酬 <= ret_5d_max（rally exhaustion 過濾，lesson #19 family
   v10/v12 cross-asset port from TSM-011 Att3）**
9. 冷卻 cooldown_days 個交易日

設計依據：lesson #19 family v10/v12 cross-strategy 鏡像擴展（TSM-011 Att3
首次發現 momentum CEILING 方向），repo 首次跨資產移植至 MBPC 框架。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_017_signal_day_filter.config import NVDA017Config

logger = logging.getLogger(__name__)


class NVDA017SignalDayFilterDetector(BaseSignalDetector):
    """NVDA-017 訊號偵測器"""

    def __init__(self, config: NVDA017Config):
        self.config = config

    @staticmethod
    def _compute_rsi(close: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.where(avg_loss > 0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Donchian breakout freshness ===
        donchian = df["High"].shift(1).rolling(self.config.donchian_period).max()
        df["Donchian_Upper"] = donchian
        df["IsNewHigh"] = df["High"] > donchian
        recency = self.config.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # === SMA trend filter (NVDA-009) ===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === Multi-week SMA regime (lesson #22) ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === Pullback from recent high ===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === RSI(14) ===
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # === ATR regime ===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === Signal-day 5d return (NVDA-017 新增 rally exhaustion 過濾) ===
        df["Ret_5d"] = df["Close"].pct_change(5)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        cond_pullback_min = df["Pullback"] <= self.config.pullback_min
        cond_pullback_max = df["Pullback"] >= self.config.pullback_max
        cond_rsi_min = df["RSI"] >= self.config.rsi_min
        cond_rsi_max = df["RSI"] <= self.config.rsi_max
        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        # NVDA-017 新增：訊號日 5 日報酬 CEILING（rally exhaustion 過濾）
        cond_ret_5d = df["Ret_5d"] <= self.config.ret_5d_max

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_regime_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
            & cond_regime_vol
            & cond_ret_5d
        )

        if self.config.bullish_close_required:
            signal = signal & (df["Close"] > df["Open"])

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
                "NVDA-017: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-017: Detected %d signals (5d ceiling %.3f)",
            signal_count,
            self.config.ret_5d_max,
        )
        return df

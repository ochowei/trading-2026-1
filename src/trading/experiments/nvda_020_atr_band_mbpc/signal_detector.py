"""
NVDA-020 訊號偵測器：Volatility-Acceleration Band Filter on Regime-Aware MBPC

進場條件（全部滿足）：
1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
2. Close > SMA(sma_trend_period)
3. SMA(sma_regime_short) ≥ sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered multi-week SMA regime gate）
4. 5 日高點回檔在 [pullback_max, pullback_min]
5. RSI(rsi_period) ∈ [rsi_min, rsi_max]
6. Close > Open（多頭 K 棒確認）
7. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （NVDA-013 multi-week vol regime）
8. **入場日波動加速 BAND**：
   atr_band_floor < ATR(atr_band_short) / ATR(atr_band_long) ≤ atr_band_ceiling
   （NVDA-020 新增；CIBR-014 / FXI-014 跨資產移植）
9. 冷卻 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_020_atr_band_mbpc.config import NVDA020Config

logger = logging.getLogger(__name__)


class NVDA020ATRBandMBPCDetector(BaseSignalDetector):
    """NVDA-020 訊號偵測器"""

    def __init__(self, config: NVDA020Config):
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

        # === SMA trend filter ===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === Multi-week SMA regime ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === Pullback from recent high ===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === RSI(14) ===
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # === True Range ===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # === Multi-week ATR regime（NVDA-013 既有）===
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === 入場日 ATR ratio BAND（NVDA-020 新增）===
        df["ATR_Band_Short"] = df["TR"].rolling(self.config.atr_band_short).mean()
        df["ATR_Band_Long"] = df["TR"].rolling(self.config.atr_band_long).mean()
        df["ATR_Band_Ratio"] = df["ATR_Band_Short"] / df["ATR_Band_Long"].where(
            df["ATR_Band_Long"] > 0, float("nan")
        )

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

        if self.config.use_atr_band:
            cond_atr_band_floor = df["ATR_Band_Ratio"] > self.config.atr_band_floor
            cond_atr_band_ceiling = df["ATR_Band_Ratio"] <= self.config.atr_band_ceiling
            cond_atr_band = cond_atr_band_floor & cond_atr_band_ceiling
        else:
            cond_atr_band = pd.Series(True, index=df.index)

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_regime_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
            & cond_regime_vol
            & cond_atr_band
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
                "NVDA-020: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-020: Detected %d ATR-Band-filtered MBPC signals",
            signal_count,
        )
        return df

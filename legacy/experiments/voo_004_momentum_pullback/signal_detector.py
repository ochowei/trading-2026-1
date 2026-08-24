"""
VOO-004 Signal Detector: Momentum Breakout Pullback Continuation

進場條件（全部滿足）：
    1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
    2. Close > SMA(sma_trend_period)
    3. （可選）Close > SMA(sma_long_period)
    4. 當前 Close 相對於 pullback_lookback 日高點回檔在 [pullback_max, pullback_min]
    5. RSI(rsi_period) ∈ [rsi_min, rsi_max]
    6. Close > Open（多頭 K 棒確認）
    7. （可選）ATR(5)/ATR(20) >= atr_ratio_min
    8. 冷卻 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.voo_004_momentum_pullback.config import VOO004Config

logger = logging.getLogger(__name__)


class VOO004SignalDetector(BaseSignalDetector):
    """VOO-004 Momentum Breakout Pullback Continuation 訊號偵測器"""

    def __init__(self, config: VOO004Config):
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

    @staticmethod
    def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
        prev_close = df["Close"].shift(1)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr.rolling(period).mean()

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian upper (shift(1) avoids look-ahead): prior N-day high
        donchian = df["High"].shift(1).rolling(self.config.donchian_period).max()
        df["Donchian_Upper"] = donchian

        # New-high flag: today's High breaks above prior N-day high
        df["IsNewHigh"] = df["High"] > donchian

        # Breakout freshness: any new-high in the last `breakout_recency_days`
        recency = self.config.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # SMA trend filter
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        # Pullback from recent high
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(14)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # ATR ratio (Att3)
        atr5 = self._compute_atr(df, 5)
        atr20 = self._compute_atr(df, 20)
        df["ATR_Ratio"] = atr5 / atr20

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_long_trend = (
            df["Close"] > df["SMA_Long"]
            if self.config.require_above_sma_long
            else pd.Series(True, index=df.index)
        )
        cond_pullback_min = df["Pullback"] <= self.config.pullback_min
        cond_pullback_max = df["Pullback"] >= self.config.pullback_max
        cond_rsi_min = df["RSI"] >= self.config.rsi_min
        cond_rsi_max = df["RSI"] <= self.config.rsi_max
        cond_atr = (
            df["ATR_Ratio"] >= self.config.atr_ratio_min
            if self.config.require_atr_ratio
            else pd.Series(True, index=df.index)
        )

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_long_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
            & cond_atr
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
                "VOO-004: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "VOO-004: Detected %d momentum breakout pullback continuation signals",
            signal_count,
        )
        return df

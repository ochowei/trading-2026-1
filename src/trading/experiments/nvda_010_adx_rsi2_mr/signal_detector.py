"""
NVDA-010 Signal Detector: ADX-Filtered RSI(2) Mean Reversion

進場條件（全部滿足）：
    1. ADX(14) >= adx_threshold（強趨勢確認）
    2. +DI(14) > -DI(14)（多頭方向確認）
    3. Close > SMA(sma_trend_period)（中期趨勢過濾）
    4. RSI(rsi_period) <= rsi_threshold（短期超賣觸發）
    5. 5 日 Pullback ∈ [pullback_max, pullback_min]
    6. Close > Open（當日多頭 K 棒）
    7. 冷卻 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_010_adx_rsi2_mr.config import NVDA010Config

logger = logging.getLogger(__name__)


class NVDA010SignalDetector(BaseSignalDetector):
    """NVDA-010 ADX-Filtered RSI(2) MR 訊號偵測器"""

    def __init__(self, config: NVDA010Config):
        self.config = config

    @staticmethod
    def _wilder_ema(series: pd.Series, period: int) -> pd.Series:
        """Wilder smoothing: EMA with alpha = 1/period."""
        return series.ewm(alpha=1 / period, adjust=False).mean()

    @classmethod
    def _compute_rsi(cls, close: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI."""
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = cls._wilder_ema(gain, period)
        avg_loss = cls._wilder_ema(loss, period)
        rs = avg_gain / avg_loss.where(avg_loss > 0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    @classmethod
    def _compute_adx_dmi(
        cls, high: pd.Series, low: pd.Series, close: pd.Series, period: int
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Wilder's ADX, +DI, -DI.

        Returns (adx, plus_di, minus_di), all on a 0-100 scale.
        """
        prev_close = close.shift(1)
        tr = pd.concat(
            [
                (high - low).abs(),
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = ((up_move > down_move) & (up_move > 0)).astype(float) * up_move.clip(lower=0.0)
        minus_dm = ((down_move > up_move) & (down_move > 0)).astype(float) * down_move.clip(
            lower=0.0
        )

        atr = cls._wilder_ema(tr, period)
        plus_di = 100 * cls._wilder_ema(plus_dm, period) / atr.where(atr > 0, float("nan"))
        minus_di = 100 * cls._wilder_ema(minus_dm, period) / atr.where(atr > 0, float("nan"))

        di_sum = plus_di + minus_di
        dx = 100 * (plus_di - minus_di).abs() / di_sum.where(di_sum > 0, float("nan"))
        adx = cls._wilder_ema(dx.fillna(0.0), period)

        return adx.fillna(0.0), plus_di.fillna(0.0), minus_di.fillna(0.0)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # ADX / DMI
        adx, plus_di, minus_di = self._compute_adx_dmi(
            df["High"], df["Low"], df["Close"], self.config.adx_period
        )
        df["ADX"] = adx
        df["PlusDI"] = plus_di
        df["MinusDI"] = minus_di

        # RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # SMA trend filter
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # Pullback from recent N-day high
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_adx_strong = df["ADX"] >= self.config.adx_threshold
        cond_dmi_bullish = (
            df["PlusDI"] > df["MinusDI"]
            if self.config.require_bullish_dmi
            else pd.Series(True, index=df.index)
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_rsi = df["RSI"] <= self.config.rsi_threshold
        cond_pullback_min = df["Pullback"] <= self.config.pullback_min
        cond_pullback_max = df["Pullback"] >= self.config.pullback_max

        signal = (
            cond_adx_strong
            & cond_dmi_bullish
            & cond_trend
            & cond_rsi
            & cond_pullback_min
            & cond_pullback_max
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
            logger.info("NVDA-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-010: Detected %d ADX-filtered RSI(2) MR signals",
            signal_count,
        )
        return df

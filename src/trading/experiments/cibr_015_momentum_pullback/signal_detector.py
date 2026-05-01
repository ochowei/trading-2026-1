"""
CIBR-015 Signal Detector: Momentum Breakout Pullback Continuation

進場條件（全部滿足）：
    1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
    2. Close > SMA(sma_trend_period)
    3. 當前 Close 相對於 pullback_lookback 日高點回檔在 [pullback_max, pullback_min]
    4. RSI(rsi_period) ∈ [rsi_min, rsi_max]
    5. Close > Open（多頭 K 棒確認）
    6. （可選）SMA(sma_regime_short) >= sma_regime_k_min × SMA(sma_regime_long)
       若 require_sma_regime_box：另需 SMA(short) <= sma_regime_k_max × SMA(long)
    7. 冷卻 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_015_momentum_pullback.config import CIBR015Config

logger = logging.getLogger(__name__)


class CIBR015SignalDetector(BaseSignalDetector):
    """CIBR-015 Momentum Breakout Pullback Continuation 訊號偵測器"""

    def __init__(self, config: CIBR015Config):
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
        cfg = self.config

        # Donchian upper (shift(1) 避免 look-ahead): prior N 日最高價
        donchian = df["High"].shift(1).rolling(cfg.donchian_period).max()
        df["Donchian_Upper"] = donchian

        # 新高 flag：今日 High 突破前 N 日最高價
        df["IsNewHigh"] = df["High"] > donchian

        # Breakout freshness：近 breakout_recency_days 日內出現新高
        recency = cfg.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # SMA 中期趨勢
        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        # 5 日高點回檔
        n = cfg.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(14)
        df["RSI"] = self._compute_rsi(df["Close"], cfg.rsi_period)

        # Multi-week SMA regime ratio (lesson #22 cross-strategy 移植)
        df["SMA_Regime_Short"] = df["Close"].rolling(cfg.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(cfg.sma_regime_long).mean()
        df["SMA_Regime_Ratio"] = df["SMA_Regime_Short"] / df["SMA_Regime_Long"].where(
            df["SMA_Regime_Long"] > 0, float("nan")
        )

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_pullback_min = df["Pullback"] <= cfg.pullback_min
        cond_pullback_max = df["Pullback"] >= cfg.pullback_max
        cond_rsi_min = df["RSI"] >= cfg.rsi_min
        cond_rsi_max = df["RSI"] <= cfg.rsi_max

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
        )

        if cfg.bullish_close_required:
            signal = signal & (df["Close"] > df["Open"])

        if cfg.require_sma_regime:
            cond_regime_min = df["SMA_Regime_Ratio"] >= cfg.sma_regime_k_min
            signal = signal & cond_regime_min
            if cfg.require_sma_regime_box:
                cond_regime_max = df["SMA_Regime_Ratio"] <= cfg.sma_regime_k_max
                signal = signal & cond_regime_max

        df["Signal"] = signal.fillna(False)

        # Cooldown
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
                "CIBR-015: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "CIBR-015: Detected %d momentum breakout pullback continuation signals",
            signal_count,
        )
        return df

"""
EEM-007 訊號偵測器（Att3）：牛市政權過濾均值回歸

進場條件（全部滿足）：
1. 收盤價 > SMA(200)（牛市政權確認）
2. RSI(2) < 10（極端超賣）
3. 2 日累計跌幅 >= 1.5%（急跌確認）
4. ClosePos >= 40%（日內反轉確認）
5. ATR(5)/ATR(20) > 1.15（波動率飆升）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_007_trend_momentum_pullback.config import EEM007Config

logger = logging.getLogger(__name__)


class EEM007SignalDetector(BaseSignalDetector):
    def __init__(self, config: EEM007Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # SMA(200) regime filter
        df["SMA_Regime"] = df["Close"].rolling(self.config.regime_sma_period).mean()

        # RSI(2)
        period = self.config.rsi_period
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # 2-day cumulative decline
        df["Decline_2d"] = df["Close"].pct_change(self.config.decline_days)

        # Close Position (where close is within day's range)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Short"] = tr.rolling(self.config.atr_short).mean()
        df["ATR_Long"] = tr.rolling(self.config.atr_long).mean()
        df["ATR_Ratio"] = df["ATR_Short"] / df["ATR_Long"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_regime = df["Close"] > df["SMA_Regime"]
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= -self.config.decline_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_regime & cond_rsi & cond_decline & cond_closepos & cond_atr

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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
        logger.info("EEM-007: Detected %d regime-filtered mean reversion signals", signal_count)
        return df

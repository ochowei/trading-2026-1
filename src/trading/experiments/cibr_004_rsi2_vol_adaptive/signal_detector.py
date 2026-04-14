"""
CIBR-004 訊號偵測器：RSI(2) 波動率自適應均值回歸

進場條件（全部滿足）：
1. RSI(2) < 10（極端超賣）
2. 2日累計跌幅 >= 2.0%（幅度過濾）
3. 收盤位置 >= 40%（日內反轉確認）
4. ATR(5)/ATR(20) > 1.15（波動率急升過濾）
5. 冷卻期 5 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_004_rsi2_vol_adaptive.config import CIBRRSI2Config

logger = logging.getLogger(__name__)


class CIBRRSI2SignalDetector(BaseSignalDetector):
    def __init__(self, config: CIBRRSI2Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2日累計跌幅
        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_rsi & cond_decline & cond_reversal & cond_vol

        # Cooldown mechanism
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
                "CIBR-004: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("CIBR-004: Detected %d RSI(2) vol-adaptive signals", signal_count)
        return df

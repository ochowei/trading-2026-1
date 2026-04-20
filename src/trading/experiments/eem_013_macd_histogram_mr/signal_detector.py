"""
EEM-013 訊號偵測器：MACD 柱狀圖多頭轉折 + 回檔混合進場均值回歸

進場條件（全部滿足）：
1. MACD(12, 26, 9) 柱狀圖：today > yesterday AND yesterday > day-before-yesterday
   AND yesterday < 0（兩根連續上揚仍處於負值區，賣壓衰竭動量轉折）
2. 10 日高點回檔介於 [-8%, -2%]（淺至中等回檔，避免崩盤續跌）
3. Williams %R(10) <= -75（超賣確認）
4. ClosePos >= 40%（日內反轉）
5. ATR(5)/ATR(20) < 1.10（反向 ATR 過濾：MACD 框架偏好低波動環境，
   過濾 bear market dead-cat bounce 假訊號）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_013_macd_histogram_mr.config import EEM013Config

logger = logging.getLogger(__name__)


class EEM013SignalDetector(BaseSignalDetector):
    def __init__(self, config: EEM013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # MACD（使用標準 EMA 遞迴）
        fast = self.config.macd_fast
        slow = self.config.macd_slow
        sig = self.config.macd_signal
        ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
        df["MACD"] = ema_fast - ema_slow
        df["MACD_Signal"] = df["MACD"].ewm(span=sig, adjust=False).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

        # 10 日高點回檔
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio（反向過濾用）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        hist = df["MACD_Hist"]
        hist_prev = hist.shift(1)
        hist_prev2 = hist.shift(2)
        cond_macd_turn = (hist > hist_prev) & (hist_prev > hist_prev2) & (hist_prev < 0)
        cond_pb_floor = df["Pullback"] <= self.config.pullback_floor
        cond_pb_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        cond_atr = df["ATR_Ratio"] < self.config.atr_ratio_max

        df["Signal"] = (
            cond_macd_turn & cond_pb_floor & cond_pb_cap & cond_wr & cond_reversal & cond_atr
        )

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
            logger.info("EEM-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("EEM-013: Detected %d MACD hist bullish-turn signals", signal_count)
        return df

"""
CIBR-004 Att2 訊號偵測器：動量強化均值回歸

在 CIBR-002 的 pullback+WR+ClosePos+ATR 基礎上，新增 2日急跌過濾。

進場條件（全部滿足）：
1. 10日高點回檔 >= 4%（深度回檔）
2. Williams %R(10) <= -80（超賣確認）
3. 收盤位置 >= 40%（日內反轉確認）
4. ATR(5)/ATR(20) > 1.15（波動率急升）
5. 2日累計跌幅 >= 1.5%（短期動量崩潰確認）
6. 冷卻期 8 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_004_rsi2_vol_adaptive.config import CIBR004Config

logger = logging.getLogger(__name__)


class CIBR004SignalDetector(BaseSignalDetector):
    def __init__(self, config: CIBR004Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度：收盤價 vs 近 N 日最高價
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

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

        # 2日累計跌幅
        dl = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(dl)) / df["Close"].shift(dl)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold

        df["Signal"] = cond_pullback & cond_wr & cond_closepos & cond_atr & cond_decline

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
        logger.info("CIBR-004: Detected %d momentum-enhanced MR signals", signal_count)
        return df

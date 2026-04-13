"""
EWZ-003 訊號偵測器：急跌恐慌反轉（Att3 策略轉向）

進場條件（全部滿足）：
1. 2 日累計跌幅 ≤ -3.5%（急性恐慌拋售）
2. Williams %R(10) ≤ -70（中期超賣確認，較 -80 放寬因 2日急跌已嚴格過濾）
3. 收盤位置 ≥ 35%（日內反轉確認）
4. ATR(5)/ATR(20) > 1.1（波動率飆升，過濾慢磨下跌）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewz_003_bb_squeeze_breakout.config import EWZ003Config

logger = logging.getLogger(__name__)


class EWZ003SignalDetector(BaseSignalDetector):
    def __init__(self, config: EWZ003Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 2-day cumulative return
        df["Return_2d"] = df["Close"].pct_change(2)

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # Close position (intraday reversal)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR ratio: short-term vs long-term volatility
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
        df["ATR_Ratio"] = atr_short / atr_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_decline = df["Return_2d"] <= self.config.decline_2d_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_decline & cond_wr & cond_reversal & cond_vol

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

        signal_count = df["Signal"].sum()
        logger.info("EWZ-003: Detected %d acute panic reversal signals", signal_count)
        return df

"""
EWT-006 訊號偵測器：出場優化均值回歸

進場條件（全部滿足）：
1. 10 日高點回檔 >= 4%（深度過濾）
2. 回檔 <= 10%（隔離極端崩盤）
3. Williams %R(10) <= -80（超賣確認）
4. 收盤位置 >= 40%（日內反轉確認）
5. ATR(5) / ATR(20) > 1.15（波動率飆升過濾）
6. 2日報酬 <= -1.5%（急跌確認，過濾慢磨下跌）
7. 冷卻期 8 個交易日

與 EWT-004 差異：出場參數優化（TP +3.5%/SL -4.5%/15d vs TP +5.0%/SL -4.5%/20d）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewt_006_optimized_exit_mr.config import EWT006Config

logger = logging.getLogger(__name__)


class EWT006SignalDetector(BaseSignalDetector):
    def __init__(self, config: EWT006Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日高點回檔
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 收盤位置
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

        # 2日報酬
        df["Return_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold

        df["Signal"] = cond_pullback & cond_cap & cond_wr & cond_reversal & cond_vol & cond_drop

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
        logger.info("EWT-006: Detected %d optimized-exit pullback signals", signal_count)
        return df

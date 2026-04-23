"""
FCX-012 Donchian Lower Washout + Intraday Reversal MR 訊號偵測器

進場條件（全部滿足）：
1. Close 距 20 日低點 <= 2.5%（Close 接近最新 Donchian 下緣）
2. 今日或昨日 Low = 20 日低點（最近一次真實洗盤確認）
3. ClosePos >= 40%（日內反轉）
4. ATR(5)/ATR(20) >= 1.10（波動率放大，panic 確認）
5. 60 日回撤 ∈ [-30%, -10%]（中等深度，排除淺漂移與結構性崩潰）
6. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_012_donchian_low_washout.config import FCX012Config

logger = logging.getLogger(__name__)


class FCX012SignalDetector(BaseSignalDetector):
    def __init__(self, config: FCX012Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Donchian Lower（20 日最低 Low）
        n = self.config.donchian_period
        df["Donchian_Low"] = df["Low"].rolling(n).min()

        # Close 相對 Donchian Low 的距離（百分比）
        df["CloseAboveLow"] = (df["Close"] - df["Donchian_Low"]) / df["Donchian_Low"]

        # 今日或昨日 Low 是否 = 20 日最低（true washout）
        df["IsNewLow"] = df["Low"] <= df["Donchian_Low"] + 1e-9
        k = self.config.washout_lookback_days
        df["RecentWashout"] = df["IsNewLow"].rolling(k).max().astype(bool)

        # ClosePos
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
        atr_fast = tr.rolling(self.config.atr_fast).mean()
        atr_slow = tr.rolling(self.config.atr_slow).mean()
        df["ATR_Ratio"] = atr_fast / atr_slow.where(atr_slow > 0, float("nan"))

        # 60 日回撤
        dd_n = self.config.drawdown_lookback
        df["High_DD"] = df["High"].rolling(dd_n).max()
        df["Drawdown"] = (df["Close"] - df["High_DD"]) / df["High_DD"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_near_low = df["CloseAboveLow"] <= self.config.close_near_low_threshold
        cond_washout = (
            df["RecentWashout"]
            if self.config.require_washout_day
            else pd.Series(True, index=df.index)
        )
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_Ratio"] >= self.config.atr_ratio_threshold
        cond_dd = (df["Drawdown"] <= self.config.drawdown_upper) & (
            df["Drawdown"] >= self.config.drawdown_lower
        )

        if self.config.require_higher_low_today:
            cond_higher_low = df["Low"] > df["Low"].shift(1)
        else:
            cond_higher_low = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_near_low & cond_washout & cond_closepos & cond_atr & cond_dd & cond_higher_low
        )

        # Cooldown
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
            logger.info("FCX-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FCX-012: Detected %d Donchian Lower Washout signals", signal_count)
        return df

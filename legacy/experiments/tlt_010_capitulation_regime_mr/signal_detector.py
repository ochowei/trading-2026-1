"""
TLT Capitulation-Confirmed Vol-Regime-Gated Mean Reversion 訊號偵測器 (TLT-010)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ≥ 3%
2. 10 日高點回檔 ≤ 7%
3. Williams %R(10) ≤ -80
4. 收盤位置 ≥ 40%（日內反轉）
5. BB(20, 2) 通道寬度 / Close < 0.05（波動率 regime 閘門）
6. 2 日累積報酬 ≤ -1.5%（capitulation 確認，新增於 TLT-010）
7. 冷卻期 7 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_010_capitulation_regime_mr.config import TLT010Config

logger = logging.getLogger(__name__)


class TLT010SignalDetector(BaseSignalDetector):
    """TLT-010：回檔 + WR + 反轉K線 + 波動率 regime 閘門 + 2 日急跌確認"""

    def __init__(self, config: TLT010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        # 2 日累積報酬（capitulation 確認）
        two_n = self.config.two_day_decline_lookback
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(two_n) - 1.0

        # ATR 波動率擴張（Att3 新增）
        prev_close = df["Close"].shift(1)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Fast"] = tr.rolling(self.config.atr_fast_period).mean()
        df["ATR_Slow"] = tr.rolling(self.config.atr_slow_period).mean()
        df["ATR_Ratio"] = df["ATR_Fast"] / df["ATR_Slow"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio
        if self.config.use_two_day_decline_filter:
            if self.config.two_day_decline_as_cap:
                cond_capitulation = df["TwoDayReturn"] >= self.config.two_day_decline_threshold
            else:
                cond_capitulation = df["TwoDayReturn"] <= self.config.two_day_decline_threshold
        else:
            cond_capitulation = pd.Series(True, index=df.index)

        if self.config.use_atr_expansion:
            cond_atr = df["ATR_Ratio"].fillna(0) >= self.config.atr_expansion_ratio_min
        else:
            cond_atr = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_regime
            & cond_capitulation
            & cond_atr
        )

        # 冷卻機制
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
            logger.info("TLT-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TLT-010: Detected %d capitulation-confirmed regime-gated signals", signal_count
        )
        return df

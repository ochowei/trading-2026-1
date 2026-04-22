"""
TLT Volatility-Regime-Gated Mean Reversion 訊號偵測器 (TLT-007)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ≥ 3%
2. 10 日高點回檔 ≤ 7%
3. Williams %R(10) ≤ -80
4. 收盤位置 ≥ 40%（日內反轉）
5. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（波動率 regime 閘門）
6. 冷卻期 7 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_007_regime_vol_gate_mr.config import TLT007Config

logger = logging.getLogger(__name__)


class TLT007SignalDetector(BaseSignalDetector):
    """TLT-007：回檔+WR+反轉K線 + 波動率 regime 閘門"""

    def __init__(self, config: TLT007Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
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
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # Bollinger Bands 寬度（波動率 regime proxy）
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        # SMA(100) 斜率（Att3 可選長線 regime 閘門）
        lt_n = self.config.long_term_sma_period
        df["LT_SMA"] = df["Close"].rolling(lt_n).mean()
        df["LT_SMA_Prev"] = df["LT_SMA"].shift(self.config.long_term_sma_slope_lookback)
        df["LT_SMA_Slope_Up"] = df["LT_SMA"] >= df["LT_SMA_Prev"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

        if self.config.require_long_term_trend_filter:
            cond_lt_trend = df["LT_SMA_Slope_Up"].fillna(False)
        else:
            cond_lt_trend = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_regime
            & cond_lt_trend
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
            logger.info("TLT-007: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-007: Detected %d regime-gated MR signals", signal_count)
        return df

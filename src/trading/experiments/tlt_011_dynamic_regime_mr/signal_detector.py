"""
TLT Dynamic BB-Width Percentile Regime MR 訊號偵測器 (TLT-011)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ≥ 3%
2. 10 日高點回檔 ≤ 7%
3. Williams %R(10) ≤ -80
4. 收盤位置 ≥ 40%（日內反轉）
5. BB(20, 2) 寬度 / Close 的 252 日 rolling percentile rank <= max_bb_width_pctile_rank
   （波動率 regime 閘門 — 相對於近 1 年分位數的動態門檻）
6. (可選) BB(20, 2) 寬度 / Close < max_bb_width_ratio_absolute（絕對上限雙閘門）
7. 冷卻期 7 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_011_dynamic_regime_mr.config import TLT011Config

logger = logging.getLogger(__name__)


class TLT011SignalDetector(BaseSignalDetector):
    """TLT-011：回檔+WR+反轉K線 + 動態 BB 寬度分位數 regime 閘門"""

    def __init__(self, config: TLT011Config):
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

        # 動態 BB 寬度 percentile rank（相對於近 N 日）
        lb = self.config.bb_width_pctile_lookback
        df["BB_Width_Pctile"] = df["BB_Width_Ratio"].rolling(lb, min_periods=lb // 2).rank(pct=True)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_regime_pctile = (df["BB_Width_Pctile"] <= self.config.max_bb_width_pctile_rank).fillna(
            False
        )

        if self.config.enable_absolute_backup:
            cond_regime_abs = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio_absolute
            cond_regime = cond_regime_pctile & cond_regime_abs
        else:
            cond_regime = cond_regime_pctile

        df["Signal"] = cond_pullback_min & cond_pullback_max & cond_wr & cond_reversal & cond_regime

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
            logger.info("TLT-011: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-011: Detected %d dynamic-regime-gated MR signals", signal_count)
        return df

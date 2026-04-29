"""
FXI-013 Volatility-Regime-Gated Mean Reversion 訊號偵測器

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 >= 5%
2. 10 日高點回檔 <= 12%（隔離 COVID / 監管極端衝擊）
3. Williams %R(10) <= -80
4. 收盤位置 >= 40%（日內反轉確認）
5. ATR(5)/ATR(20) > 1.05（波動率飆升確認）
6. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（波動率 regime 閘門，新增）
7. 冷卻期 10 天

第 6 項為本實驗與 FXI-005 的唯一差異，作為 regime 過濾器（TLT-007 成功結構移植）。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_013_regime_vol_gate_mr.config import FXI013Config

logger = logging.getLogger(__name__)


class FXI013SignalDetector(BaseSignalDetector):
    """FXI-013：FXI-005 完整進場條件 + BB 寬度 regime 閘門"""

    def __init__(self, config: FXI013Config):
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

        # ATR 比率
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

        # Bollinger Bands 寬度（波動率 regime proxy，新增）
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        # 動態 regime 百分位（Att3 新增）：BB 寬度在 252 日回看期的分位排名
        # rank(pct=True) 回傳 0~1 值，0 為最低、1 為最高
        pct_lookback = self.config.bb_width_percentile_lookback
        df["BB_Width_Pct"] = df["BB_Width_Ratio"].rolling(pct_lookback).rank(pct=True)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

        if self.config.use_bb_width_percentile:
            cond_regime_pct = (
                df["BB_Width_Pct"] < self.config.bb_width_percentile_threshold
            ).fillna(False)
        else:
            cond_regime_pct = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_atr
            & cond_regime
            & cond_regime_pct
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
            logger.info(
                "FXI-013: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("FXI-013: Detected %d regime-gated MR signals", signal_count)
        return df

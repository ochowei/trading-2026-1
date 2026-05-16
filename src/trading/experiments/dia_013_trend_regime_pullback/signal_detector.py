"""
DIA-013 訊號偵測器：Strict-Bull-Regime Trend Pullback Continuation

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close > SMA(200) 且 SMA(50) > SMA(200) 且 SMA(200) 較 N 日前上升
2. Close 自 10 日高點回檔 ∈ [pullback_min, pullback_max]
3. Close > 前一日 Close（回檔轉折確認，可由 require_close_up 關閉）
4. 冷卻期 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_013_trend_regime_pullback.config import DIA013Config

logger = logging.getLogger(__name__)


class DIA013SignalDetector(BaseSignalDetector):
    """DIA-013：嚴格 secular 多頭 regime + 趨勢回檔 continuation"""

    def __init__(self, config: DIA013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["SMA_Fast"] = df["Close"].rolling(self.config.sma_fast_period).mean()
        df["SMA_Slow"] = df["Close"].rolling(self.config.sma_slow_period).mean()
        df["SMA_Slow_Rising"] = df["SMA_Slow"] > df["SMA_Slow"].shift(
            self.config.sma_slow_slope_lookback
        )

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # ATR(period) / Close — 波動率 regime 量度
        prev_close = df["Close"].shift(1)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Pct"] = tr.rolling(self.config.atr_period).mean() / df["Close"]

        df["Close_Up"] = df["Close"] > df["Close"].shift(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_regime = df["SMA_Fast"] > df["SMA_Slow"]
        if self.config.require_close_above_slow:
            cond_regime = cond_regime & (df["Close"] > df["SMA_Slow"])
        if self.config.require_sma_slow_rising:
            cond_regime = cond_regime & df["SMA_Slow_Rising"]

        if self.config.pullback_mode == "sma50_support":
            cond_pullback = df["Low"] <= df["SMA_Fast"] * (1 + self.config.sma50_proximity_pct)
        else:
            cond_pullback = (df["Pullback"] >= self.config.pullback_min) & (
                df["Pullback"] <= self.config.pullback_max
            )

        if self.config.require_close_up:
            cond_close_up = df["Close_Up"]
        else:
            cond_close_up = pd.Series(True, index=df.index)

        if self.config.use_vol_regime_gate:
            cond_vol = df["ATR_Pct"] <= self.config.max_atr_pct
        else:
            cond_vol = pd.Series(True, index=df.index)

        df["Signal"] = cond_regime & cond_pullback & cond_close_up & cond_vol

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
            logger.info("DIA-013: %d signals suppressed by cooldown", len(suppressed))

        logger.info(
            "DIA-013: Detected %d signals (strict-bull-regime trend pullback)",
            int(df["Signal"].sum()),
        )
        return df

"""
USO-029 訊號偵測器：Trend-Following Pullback Continuation

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. SMA(20) > SMA(50) 且 Close > SMA(50)（中期上升趨勢 regime）
2. ROC(60) > roc_min（長期動量為正，排除下跌趨勢反彈 / 崩盤底）
3. 10 日高點回檔 ∈ [pullback_min, pullback_max]（溫和拉回）
4. Close > 前一日 Close（拉回後恢復跡象，可由 require_close_up 關閉）
5. 冷卻期 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_029_trend_pullback_continuation.config import USO029Config

logger = logging.getLogger(__name__)


class USO029SignalDetector(BaseSignalDetector):
    """USO-029：趨勢跟蹤回檔延續"""

    def __init__(self, config: USO029Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["SMA_Fast"] = df["Close"].rolling(self.config.sma_fast).mean()
        df["SMA_Slow"] = df["Close"].rolling(self.config.sma_slow).mean()
        df["SMA_Slow_Rising"] = df["SMA_Slow"] > df["SMA_Slow"].shift(
            self.config.sma_slow_slope_lookback
        )

        df["ROC"] = df["Close"].pct_change(self.config.roc_lookback)

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Donchian 通道上緣（前一日為止的 N 日最高 Close）→ 今日收破即新高突破
        dn = self.config.donchian_lookback
        df["Donchian_High"] = df["Close"].rolling(dn).max().shift(1)

        df["Close_Up"] = df["Close"] > df["Close"].shift(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_trend = (df["SMA_Fast"] > df["SMA_Slow"]) & (df["Close"] > df["SMA_Slow"])
        if self.config.require_sma_slow_rising:
            cond_trend = cond_trend & df["SMA_Slow_Rising"]
        if self.config.require_close_above_fast:
            cond_trend = cond_trend & (df["Close"] > df["SMA_Fast"])

        cond_momentum = df["ROC"] > self.config.roc_min
        if self.config.use_donchian_breakout:
            cond_pullback = df["Close"] > df["Donchian_High"]
        else:
            cond_pullback = (df["Pullback"] >= self.config.pullback_min) & (
                df["Pullback"] <= self.config.pullback_max
            )

        if self.config.require_close_up:
            cond_close_up = df["Close_Up"]
        else:
            cond_close_up = pd.Series(True, index=df.index)

        df["Signal"] = cond_trend & cond_momentum & cond_pullback & cond_close_up

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
            logger.info("USO-029: %d signals suppressed by cooldown", len(suppressed))

        logger.info(
            "USO-029: Detected %d signals (trend pullback continuation)",
            int(df["Signal"].sum()),
        )
        return df

"""
COPX Volume-Confirmed Capitulation MR 訊號偵測器 (COPX-018)

進場條件 (全部滿足, 訊號日為 T, 執行模型於 T+1 開盤進場):
1. 收盤價相對 20 日最高價回檔 10-20% (沿用 COPX-007)
2. Williams %R(10) <= -80 (沿用 COPX-007)
3. ATR(5) / ATR(20) > 1.05 (沿用 COPX-007 Att3 vol-adaptive)
4. **(COPX-018 新增) Volume 確認過濾器**, 三模式擇一:
   - ratio_sma: Volume / SMA(Volume, 20) >= threshold (default 1.30)
   - zscore_60: (Volume - SMA60) / Std60 >= threshold (default 1.0)
   - cum_5d_ratio: SUM(Volume, 5) / SUM(SMA20_Volume, 5) >= threshold
5. 冷卻期 12 個交易日 (沿用 COPX-007)
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_018_volume_confirmed_mr.config import COPX018Config

logger = logging.getLogger(__name__)


class COPX018SignalDetector(BaseSignalDetector):
    """COPX-018: vol-adaptive MR + volume-surge confirmation gate"""

    def __init__(self, config: COPX018Config):
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

        # COPX-018 核心: Volume-based confirmation
        v_sma = df["Volume"].rolling(self.config.volume_sma_period).mean()
        df["Vol_SMA"] = v_sma
        df["Vol_Ratio_SMA"] = df["Volume"] / v_sma

        v_sma60 = df["Volume"].rolling(self.config.volume_zscore_period).mean()
        v_std60 = df["Volume"].rolling(self.config.volume_zscore_period).std()
        df["Vol_Zscore_60"] = (df["Volume"] - v_sma60) / v_std60.where(v_std60 > 0, float("nan"))

        cum_n = self.config.volume_cum_lookback
        cum_vol = df["Volume"].rolling(cum_n).sum()
        cum_sma = v_sma.rolling(cum_n).sum()
        df["Vol_Cum_Ratio"] = cum_vol / cum_sma.where(cum_sma > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        signal = cond_pullback & cond_upper & cond_wr & cond_vol

        mode = self.config.volume_filter_mode
        if mode == "ratio_sma_floor":
            cond_volume = df["Vol_Ratio_SMA"] >= self.config.volume_ratio_threshold
        elif mode == "ratio_sma_ceil":
            cond_volume = df["Vol_Ratio_SMA"] <= self.config.volume_ratio_threshold
        elif mode == "zscore_60_floor":
            cond_volume = df["Vol_Zscore_60"] >= self.config.volume_zscore_threshold
        elif mode == "cum_5d_floor":
            cond_volume = df["Vol_Cum_Ratio"] >= self.config.volume_cum_threshold
        elif mode == "cum_5d_ceil":
            cond_volume = df["Vol_Cum_Ratio"] <= self.config.volume_cum_threshold
        else:
            raise ValueError(f"Unknown volume_filter_mode: {mode}")

        signal = signal & cond_volume.fillna(False)

        df["Signal"] = signal

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
            logger.info("COPX-018: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-018: Detected %d volume-confirmed MR signals (mode=%s)",
            signal_count,
            mode,
        )
        return df

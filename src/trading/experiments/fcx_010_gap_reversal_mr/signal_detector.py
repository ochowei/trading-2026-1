"""
FCX-010 訊號偵測器：Gap-Down 資本化 + 日內反轉均值回歸
(FCX-010 Signal Detector: Gap-Down Capitulation + Intraday Reversal MR)

進場條件（六項同時成立）：
1. 隔夜開盤跳空 (Open - PrevClose) / PrevClose <= -2.0%（銅期貨隔夜拋壓）
2. 日內收盤高於開盤 Close > Open（盤中資金撿便宜反轉）
3. 日內收盤位置 ClosePos = (Close - Low) / (High - Low) >= 50%
   （強日內反轉確認，Att2+ 加入——過濾弱反彈假訊號）
4. 10 日高點回檔 <= -6%（深回檔均值回歸訊號）
5. 10 日高點回檔 >= -18%（過濾崩盤極端值）
6. Williams %R(10) <= -80（超賣確認）

冷卻期 10 個交易日以避免連續下跌中重複觸發。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_010_gap_reversal_mr.config import FCX010Config

logger = logging.getLogger(__name__)


class FCX010SignalDetector(BaseSignalDetector):
    """FCX-010：Gap-Down 資本化 + 日內反轉 訊號偵測器"""

    def __init__(self, config: FCX010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["PrevClose"] = df["Close"].shift(1)
        df["Gap"] = (df["Open"] - df["PrevClose"]) / df["PrevClose"]

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range.where(day_range > 0, float("nan"))
        df["ClosePos"] = df["ClosePos"].fillna(0.5)

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_gap = df["Gap"] <= self.config.gap_threshold
        cond_reversal = df["Close"] > df["Open"]
        cond_close_pos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = (
            cond_gap & cond_reversal & cond_close_pos & cond_pullback & cond_upper & cond_wr
        )

        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap_days = len(df.loc[last_signal:idx]) - 1
                if gap_days <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("FCX-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FCX-010: Detected %d gap-down reversal signals", signal_count)
        return df

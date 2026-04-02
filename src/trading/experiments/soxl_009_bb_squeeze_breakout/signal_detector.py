"""
SOXL BB 擠壓突破訊號偵測模組
SOXL BB Squeeze Breakout Signal Detector

偵測 Bollinger Band 波動收縮後的突破訊號。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.soxl_009_bb_squeeze_breakout.config import (
    SOXLBBSqueezeConfig,
)

logger = logging.getLogger(__name__)


class SOXLBBSqueezeDetector(BaseSignalDetector):
    """
    SOXL BB 擠壓突破訊號偵測器

    條件同時成立時觸發訊號:
    1. BB Width 在過去 60 日內處於 25th 百分位以下（波動收縮）
    2. 5 日內曾出現上述擠壓
    3. Close > Upper BB（向上突破）
    4. Close > SMA(50)（趨勢確認）
    """

    def __init__(self, config: SOXLBBSqueezeConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算 BB 與趨勢指標"""
        df = df.copy()
        cfg = self.config

        # Bollinger Bands
        df["BB_Mid"] = df["Close"].rolling(window=cfg.bb_period).mean()
        bb_std = df["Close"].rolling(window=cfg.bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + cfg.bb_std * bb_std
        df["BB_Lower"] = df["BB_Mid"] - cfg.bb_std * bb_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # 擠壓偵測：BB Width 在 60 日的百分位排名
        df["BB_Width_Pctile"] = (
            df["BB_Width"]
            .rolling(window=cfg.bb_squeeze_percentile_window)
            .apply(lambda x: (x.iloc[-1] <= x).sum() / len(x) if len(x) > 0 else 1.0, raw=False)
        )

        # 當日是否為擠壓日
        df["Is_Squeeze"] = df["BB_Width_Pctile"] <= cfg.bb_squeeze_percentile

        # 5 日內是否曾出現擠壓
        df["Recent_Squeeze"] = (
            df["Is_Squeeze"]
            .rolling(window=cfg.bb_squeeze_recent_days, min_periods=1)
            .max()
            .astype(bool)
        )

        # 趨勢確認
        df["SMA_Trend"] = df["Close"].rolling(window=cfg.sma_trend_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測 BB 擠壓突破訊號"""
        df = df.copy()
        cfg = self.config

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_squeeze & cond_breakout & cond_trend

        # 冷卻機制
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info(f"[SOXLBBSqueezeDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號")

        signal_count = df["Signal"].sum()
        logger.info(f"[SOXLBBSqueezeDetector] SOXL: 偵測到 {signal_count} 個 BB 擠壓突破訊號")
        return df

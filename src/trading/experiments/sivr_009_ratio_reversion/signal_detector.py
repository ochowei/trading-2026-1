"""
SIVR-009 訊號偵測器：Gold/Silver Ratio Mean Reversion
SIVR-009 Signal Detector: Gold/Silver Ratio Mean Reversion

進場條件（全部滿足）：
1. GLD/SIVR 價格比率 z-score (60日) >= 1.5（白銀相對黃金便宜）
2. 10日高點回檔 7-15%（絕對價格下跌確認，過濾邊際訊號和極端崩盤）
3. Williams %R(10) <= -80（SIVR 超賣，短期時機確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_009_ratio_reversion.config import (
    SIVRRatioReversionConfig,
)

logger = logging.getLogger(__name__)


class SIVRRatioReversionDetector(BaseSignalDetector):
    """
    Gold/Silver Ratio Mean Reversion 訊號偵測器

    使用 GLD/SIVR 價格比率的 z-score 作為主要訊號，
    搭配 Williams %R 作為短期超賣確認。
    """

    def __init__(self, config: SIVRRatioReversionConfig):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的（GLD）數據"""
        try:
            df = yf.download(
                self.config.reference_ticker,
                start=start_date,
                progress=False,
                auto_adjust=True,
            )
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception:
            logger.exception("Failed to fetch %s data", self.config.reference_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 下載 GLD 數據
        start_date = df.index[0].strftime("%Y-%m-%d")
        gld_df = self._fetch_reference_data(start_date)

        if gld_df is None or gld_df.empty:
            logger.error("無法取得 GLD 數據，無法計算比率")
            df["Ratio_Zscore"] = 0.0
            df["WR"] = 0.0
            return df

        # 對齊日期（取交集）
        common_idx = df.index.intersection(gld_df.index)
        df = df.loc[common_idx]

        # 計算 GLD/SIVR 價格比率
        df["GLD_Close"] = gld_df.loc[common_idx, "Close"].values
        df["Ratio"] = df["GLD_Close"] / df["Close"]

        # 計算比率的滾動 z-score
        lookback = self.config.ratio_lookback
        ratio_mean = df["Ratio"].rolling(lookback).mean()
        ratio_std = df["Ratio"].rolling(lookback).std()
        df["Ratio_Zscore"] = (df["Ratio"] - ratio_mean) / ratio_std

        # 10日回檔幅度
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：比率 z-score 偏高（白銀相對便宜）
        cond_ratio = df["Ratio_Zscore"] >= self.config.ratio_zscore_threshold

        # 條件二：回檔幅度下限
        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold

        # 條件三：回檔幅度上限（過濾極端崩盤）
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap

        # 條件四：Williams %R 超賣
        cond_wr = df["WR"] <= self.config.wr_threshold

        df["Signal"] = cond_ratio & cond_pullback_min & cond_pullback_cap & cond_wr

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
            logger.info("SIVR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("SIVR: Detected %d Ratio Reversion signals", signal_count)
        return df

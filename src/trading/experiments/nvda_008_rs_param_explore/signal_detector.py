"""
NVDA-008 訊號偵測器：RS Parameter Exploration
NVDA-008 Signal Detector: RS Parameter Exploration

進場條件（全部滿足）：
1. NVDA N日報酬 - 基準 N日報酬 >= RS 門檻（相對超額表現）
2. M日高點回撤在指定範圍（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_008_rs_param_explore.config import (
    NVDARSParamExploreConfig,
)

logger = logging.getLogger(__name__)


class NVDARSParamExploreDetector(BaseSignalDetector):
    """NVDA RS Parameter Exploration 訊號偵測器"""

    def __init__(self, config: NVDARSParamExploreConfig):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的數據"""
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

        start_date = df.index[0].strftime("%Y-%m-%d")
        ref_df = self._fetch_reference_data(start_date)

        if ref_df is None or ref_df.empty:
            logger.error(
                "無法取得 %s 數據，無法計算相對強度",
                self.config.reference_ticker,
            )
            df["Relative_Strength"] = 0.0
            df["Pullback"] = 0.0
            df["SMA_Trend"] = df["Close"]
            return df

        common_idx = df.index.intersection(ref_df.index)
        df = df.loc[common_idx]

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # NVDA 和基準的 N日報酬
        period = self.config.relative_strength_period
        df["NVDA_Return"] = df["Close"].pct_change(period)
        df["Ref_Return"] = ref_df.loc[common_idx, "Close"].pct_change(period)

        # 相對強度 = NVDA 報酬 - 基準報酬
        df["Relative_Strength"] = df["NVDA_Return"] - df["Ref_Return"]

        # M日高點回撤
        lookback = self.config.pullback_lookback
        df["High_Recent"] = df["High"].rolling(lookback).max()
        df["Pullback"] = (df["High_Recent"] - df["Close"]) / df["High_Recent"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 相對超額表現
        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min

        # 短期回調在範圍內
        cond_pullback = (df["Pullback"] >= self.config.pullback_min) & (
            df["Pullback"] <= self.config.pullback_max
        )

        # 上升趨勢
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_rs & cond_pullback & cond_trend

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

        signal_count = df["Signal"].sum()
        logger.info("NVDA: Detected %d RS param explore signals", signal_count)
        return df

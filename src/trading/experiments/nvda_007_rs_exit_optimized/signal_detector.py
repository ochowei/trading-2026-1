"""
NVDA-007 訊號偵測器：RS Exit Optimization
NVDA-007 Signal Detector: RS Exit Optimization

進場條件完全沿用 NVDA-006 Att1（全部滿足）：
1. NVDA 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-8%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_007_rs_exit_optimized.config import (
    NVDARSExitOptimizedConfig,
)

logger = logging.getLogger(__name__)


class NVDARSExitOptimizedDetector(BaseSignalDetector):
    """NVDA RS Exit Optimization 訊號偵測器"""

    def __init__(self, config: NVDARSExitOptimizedConfig):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的（SMH）數據"""
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
        smh_df = self._fetch_reference_data(start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            return df

        common_idx = df.index.intersection(smh_df.index)
        df = df.loc[common_idx]

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # NVDA 和 SMH 的 20日報酬
        period = self.config.relative_strength_period
        df["NVDA_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)

        # 相對強度 = NVDA 報酬 - SMH 報酬
        df["Relative_Strength"] = df["NVDA_Return"] - df["SMH_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # NVDA 相對 SMH 有超額表現
        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min

        # 短期回調在範圍內
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
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
        logger.info("NVDA: Detected %d RS exit optimized signals", signal_count)
        return df

"""
EEM-006 訊號偵測器：RS Momentum Pullback
EEM-006 Signal Detector: Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. EEM 20日報酬 - SPY 20日報酬 >= 3%（EM 相對 DM 超額表現）
2. 5日高點回撤 2-4%（短暫整理，非崩盤）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_006_rs_momentum_pullback.config import (
    EEMRSMomentumConfig,
)

logger = logging.getLogger(__name__)


class EEMRSMomentumDetector(BaseSignalDetector):
    """EEM RS Momentum Pullback 訊號偵測器"""

    def __init__(self, config: EEMRSMomentumConfig):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的（SPY）數據"""
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

        # 下載 SPY 數據
        start_date = df.index[0].strftime("%Y-%m-%d")
        spy_df = self._fetch_reference_data(start_date)

        if spy_df is None or spy_df.empty:
            logger.error("無法取得 SPY 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            return df

        # 對齊日期（取交集）
        common_idx = df.index.intersection(spy_df.index)
        df = df.loc[common_idx]

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # EEM 和 SPY 的 20日報酬
        period = self.config.relative_strength_period
        df["EEM_Return"] = df["Close"].pct_change(period)
        df["SPY_Return"] = spy_df.loc[common_idx, "Close"].pct_change(period)

        # 相對強度 = EEM 報酬 - SPY 報酬
        df["Relative_Strength"] = df["EEM_Return"] - df["SPY_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # EEM 相對 SPY 有超額表現
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
        logger.info("EEM: Detected %d relative strength momentum signals", signal_count)
        return df

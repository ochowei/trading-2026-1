"""
EWZ-005 訊號偵測器：Relative Strength Momentum Pullback

進場條件（全部滿足）：
1. EWZ 10日報酬 - EEM 10日報酬 >= 4%（巴西相對 EM 超額表現）
2. 5日高點回撤 2-5%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewz_005_rs_momentum.config import EWZ005Config

logger = logging.getLogger(__name__)


class EWZ005SignalDetector(BaseSignalDetector):
    """EWZ Relative Strength Momentum Pullback 訊號偵測器"""

    def __init__(self, config: EWZ005Config):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的（EEM）數據"""
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

        # 下載 EEM 數據
        start_date = df.index[0].strftime("%Y-%m-%d")
        ref_df = self._fetch_reference_data(start_date)

        if ref_df is None or ref_df.empty:
            logger.error("無法取得 %s 數據，無法計算相對強度", self.config.reference_ticker)
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            return df

        # 對齊日期（取交集）
        common_idx = df.index.intersection(ref_df.index)
        df = df.loc[common_idx]

        # SMA trend
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # EWZ 和 EEM 的報酬
        period = self.config.relative_strength_period
        df["EWZ_Return"] = df["Close"].pct_change(period)
        df["EEM_Return"] = ref_df.loc[common_idx, "Close"].pct_change(period)

        # 相對強度 = EWZ 報酬 - EEM 報酬
        df["Relative_Strength"] = df["EWZ_Return"] - df["EEM_Return"]

        # 5日高點回撤
        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # EWZ 相對 EEM 有超額表現
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
        logger.info("EWZ-005: Detected %d relative strength signals", signal_count)
        return df

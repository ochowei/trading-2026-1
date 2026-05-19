"""
TSM-022 訊號偵測器：^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback

進場條件（全部滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 訊號日 5 日報酬 <= ret_5d_max（rally exhaustion 過濾，TSM-011 Att3 沿用）
5. 訊號日 ^VXN vxn_lookback 日變化 <= vxn_change_max（隱含波動率非上升 regime）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_022_vxn_implied_vol_rs.config import (
    TSMVXNImpliedVolRSConfig,
)

logger = logging.getLogger(__name__)


class TSMVXNImpliedVolRSDetector(BaseSignalDetector):
    """TSM ^VXN Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback 訊號偵測器"""

    def __init__(self, config: TSMVXNImpliedVolRSConfig):
        self.config = config

    def _fetch_series(self, ticker: str, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                ticker,
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
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        start_date = df.index[0].strftime("%Y-%m-%d")
        smh_df = self._fetch_series(self.config.reference_ticker, start_date)
        vxn_df = self._fetch_series(self.config.vxn_ticker, start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["Ret_5d"] = 0.0
            df["VXN_Change"] = 0.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        df = df.loc[common_idx]

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_5d"] = df["Close"].pct_change(5)

        if vxn_df is None or vxn_df.empty:
            logger.error("無法取得 %s 數據，^VXN gate 視為停用", self.config.vxn_ticker)
            df["VXN_Change"] = -999.0
        else:
            vxn_close = vxn_df["Close"].reindex(df.index).ffill()
            df["VXN_Change"] = vxn_close - vxn_close.shift(self.config.vxn_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max
        cond_vxn = df["VXN_Change"] <= self.config.vxn_change_max

        df["Signal"] = cond_rs & cond_pullback & cond_trend & cond_5d & cond_vxn

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
        logger.info("TSM: Detected %d filtered signals", signal_count)
        return df

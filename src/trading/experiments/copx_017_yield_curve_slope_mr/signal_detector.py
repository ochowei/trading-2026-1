"""
COPX Yield-Curve-Slope Industrial-Demand-Regime-Gated MR 訊號偵測器 (COPX-017)

進場條件 (全部滿足, 訊號日為 T, 執行模型於 T+1 開盤進場):
1. 收盤價相對 20 日最高價回檔 10-20% (沿用 COPX-007)
2. Williams %R(10) <= -80 (沿用 COPX-007)
3. ATR(5) / ATR(20) > 1.05 (沿用 COPX-007 Att3 vol-adaptive)
4. **(COPX-017 新增) (^TYX - ^TNX) N 日變化 >= min_slope_change**
   yield curve 30Y-10Y slope velocity, forward-looking industrial demand
   regime gate (filter out rapid flattening = recession fear escalation)
5. 冷卻期 12 個交易日 (沿用 COPX-007)
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_017_yield_curve_slope_mr.config import COPX017Config

logger = logging.getLogger(__name__)


class COPX017SignalDetector(BaseSignalDetector):
    """COPX-017: vol-adaptive MR + yield curve slope velocity regime gate"""

    def __init__(self, config: COPX017Config):
        self.config = config

    def _fetch_external(self, ticker: str, start_date: str) -> pd.DataFrame | None:
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

        # COPX-017 核心: yield curve slope velocity (^TYX - ^TNX)
        start_date = df.index[0].strftime("%Y-%m-%d")
        long_yield_df = self._fetch_external(self.config.long_yield_ticker, start_date)
        short_yield_df = self._fetch_external(self.config.short_yield_ticker, start_date)
        if (
            long_yield_df is None
            or long_yield_df.empty
            or short_yield_df is None
            or short_yield_df.empty
        ):
            logger.error(
                "無法取得 %s / %s 數據, yield curve slope 過濾停用",
                self.config.long_yield_ticker,
                self.config.short_yield_ticker,
            )
            df["Yield_Slope"] = float("nan")
            df["Slope_Change_N"] = 0.0
        else:
            long_yield = long_yield_df["Close"].reindex(df.index, method="ffill")
            short_yield = short_yield_df["Close"].reindex(df.index, method="ffill")
            slope = long_yield - short_yield
            df["Yield_Slope"] = slope
            df["Slope_Change_N"] = slope.diff(self.config.slope_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        signal = cond_pullback & cond_upper & cond_wr & cond_vol

        if self.config.use_slope_change_filter:
            cond_slope_change = df["Slope_Change_N"] >= self.config.min_slope_change
            signal = signal & cond_slope_change

        if self.config.use_slope_level_filter:
            cond_slope_level = df["Yield_Slope"] >= self.config.min_slope_level
            signal = signal & cond_slope_level

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
            logger.info("COPX-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-017: Detected %d yield-curve-slope-gated MR signals",
            signal_count,
        )
        return df

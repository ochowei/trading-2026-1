"""
TLT Yield-Curve-Slope Inflation-Regime-Gated MR 訊號偵測器 (TLT-017)

進場條件 (全部滿足, 訊號日為 T, 執行模型於 T+1 開盤進場):
1. 10 日高點回檔 ≥ 3% 且 ≤ 7% (沿用 TLT-014)
2. Williams %R(10) ≤ -80 (沿用 TLT-014)
3. 收盤位置 ≥ 40% (沿用 TLT-014)
4. BB(20, 2) 寬度 / Close < 5% (沿用 TLT-007 / TLT-014)
5. ^MOVE 收盤值 ≤ 130 (LEVEL CAP, 沿用 TLT-013 Att1 / TLT-014)
6. TLT 20d 報酬 - SPY 20d 報酬 ≥ -4% (cross-asset divergence, 沿用 TLT-014 Att3)
7. **(TLT-017 新增) (^TYX - ^TNX) N 日變化 ≤ max_slope_change**
   yield curve 30Y-10Y slope velocity, forward-looking inflation expectation regime
8. 冷卻期 7 天
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_017_yield_curve_slope_mr.config import TLT017Config

logger = logging.getLogger(__name__)


class TLT017SignalDetector(BaseSignalDetector):
    """TLT-017: BB-width + ^MOVE LEVEL + TLT-SPY divergence + yield curve slope
    velocity regime gate MR"""

    def __init__(self, config: TLT017Config):
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

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        div_n = self.config.divergence_lookback
        df["TLT_Ret_N"] = df["Close"].pct_change(div_n)

        start_date = df.index[0].strftime("%Y-%m-%d")

        move_df = self._fetch_external(self.config.move_ticker, start_date)
        if move_df is None or move_df.empty:
            logger.error("無法取得 %s 數據, ^MOVE 過濾停用", self.config.move_ticker)
            df["MOVE_Close"] = float("nan")
        else:
            df["MOVE_Close"] = move_df["Close"].reindex(df.index, method="ffill")

        bench_df = self._fetch_external(self.config.benchmark_ticker, start_date)
        if bench_df is None or bench_df.empty:
            logger.error(
                "無法取得 %s 數據, cross-asset divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["Bench_Close"] = float("nan")
            df["Bench_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            bench_close = bench_df["Close"].reindex(df.index, method="ffill")
            df["Bench_Close"] = bench_close
            df["Bench_Ret_N"] = bench_close.pct_change(div_n)
            df["Rel_Return_N"] = df["TLT_Ret_N"] - df["Bench_Ret_N"]

        # TLT-017 核心: yield curve slope velocity (^TYX - ^TNX)
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

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_bb_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio
        cond_move_level = df["MOVE_Close"] <= self.config.max_move_level
        cond_divergence = df["Rel_Return_N"] >= self.config.min_relative_return
        cond_slope = df["Slope_Change_N"] <= self.config.max_slope_change

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_bb_regime
            & cond_move_level
            & cond_divergence
            & cond_slope
        )

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
            logger.info("TLT-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TLT-017: Detected %d yield-curve-slope-gated MR signals",
            signal_count,
        )
        return df

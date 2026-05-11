"""
TLT ^MOVE Multi-Window IV Direction Regime-Gated MR 訊號偵測器 (TLT-016)

進場條件 (全部滿足, 訊號日為 T, 執行模型於 T+1 開盤進場):
1. 10 日高點回檔 ≥ 3% 且 ≤ 7% (沿用 TLT-014)
2. Williams %R(10) ≤ -80 (沿用 TLT-014)
3. 收盤位置 ≥ 40% (沿用 TLT-014)
4. BB(20, 2) 寬度 / Close < 5% (沿用 TLT-007 / TLT-014)
5. ^MOVE 收盤值 ≤ 130 (LEVEL CAP, 沿用 TLT-013 Att1 / TLT-014)
6. TLT 20d 報酬 - SPY 20d 報酬 ≥ -4% (cross-asset divergence, 沿用 TLT-014 Att3)
7. (TLT-016 新增) ^MOVE 5d 變化 ≤ max_move_5d_change (multi-window direction)
8. (Att3 候選) ^MOVE 3d 變化 ≤ max_move_3d_change
9. 冷卻期 7 天
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_016_move_multi_window_direction_mr.config import (
    TLT016Config,
)

logger = logging.getLogger(__name__)


class TLT016SignalDetector(BaseSignalDetector):
    """TLT-016: BB-width + ^MOVE LEVEL + TLT-SPY divergence + ^MOVE multi-window
    direction regime gate MR"""

    def __init__(self, config: TLT016Config):
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
            df["MOVE_5d_Change"] = 0.0
            df["MOVE_3d_Change"] = 0.0
        else:
            move_close = move_df["Close"].reindex(df.index, method="ffill")
            df["MOVE_Close"] = move_close
            df["MOVE_5d_Change"] = move_close.diff(self.config.move_5d_lookback)
            df["MOVE_3d_Change"] = move_close.diff(self.config.move_3d_lookback)

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

        signal = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_bb_regime
            & cond_move_level
            & cond_divergence
        )

        if self.config.use_move_5d_direction_filter:
            cond_move_5d = df["MOVE_5d_Change"] <= self.config.max_move_5d_change
            signal = signal & cond_move_5d

        if self.config.use_move_3d_direction_filter:
            cond_move_3d = df["MOVE_3d_Change"] <= self.config.max_move_3d_change
            signal = signal & cond_move_3d

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
            logger.info("TLT-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TLT-016: Detected %d multi-window direction-gated MR signals",
            signal_count,
        )
        return df

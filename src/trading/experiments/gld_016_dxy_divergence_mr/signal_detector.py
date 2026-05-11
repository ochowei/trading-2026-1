"""
GLD DXY Cross-Asset Divergence Filter on GVZ-Gated MR 訊號偵測器 (GLD-016)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 收盤價低於 20 日高點 ≥ 3%
2. Williams %R(10) ≤ -80
3. 收盤位置 ≥ 40%
4. 1 日累計報酬 <= -0.3%
5. 2 日累計報酬 <= -0.5%
6. ^GVZ 10 日變化 <= +0.40（GLD-015 Att2 sweet spot）
7. DXY N 日變化 <= max_dxy_change（GLD-016 核心新增）
8. 冷卻期 7 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_016_dxy_divergence_mr.config import GLD016Config

logger = logging.getLogger(__name__)


class GLD016SignalDetector(BaseSignalDetector):
    """GLD-016：GLD-015 Att2 框架 + DXY cross-asset divergence regime gate"""

    def __init__(self, config: GLD016Config):
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
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_2d"] = df["Close"].pct_change(2)

        start_date = df.index[0].strftime("%Y-%m-%d")

        gvz_df = self._fetch_external(self.config.gvz_ticker, start_date)
        if gvz_df is None or gvz_df.empty:
            logger.error("無法取得 %s 數據，^GVZ 過濾停用", self.config.gvz_ticker)
            df["GVZ_Change_10d"] = 0.0
        else:
            gvz_close = gvz_df["Close"].reindex(df.index, method="ffill")
            df["GVZ_Change_10d"] = gvz_close.diff(self.config.gvz_direction_lookback)

        dxy_df = self._fetch_external(self.config.dxy_ticker, start_date)
        if dxy_df is None or dxy_df.empty:
            logger.error("無法取得 %s 數據，DXY 過濾停用", self.config.dxy_ticker)
            df["DXY_PctChange_Nd"] = 0.0
        else:
            dxy_close = dxy_df["Close"].reindex(df.index, method="ffill")
            df["DXY_PctChange_Nd"] = dxy_close.pct_change(self.config.dxy_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_floor = df["Return_1d"] <= self.config.oneday_return_floor
        cond_twoday_floor = df["Return_2d"] <= self.config.twoday_return_floor
        cond_gvz = df["GVZ_Change_10d"] <= self.config.max_gvz_direction_change
        cond_dxy = df["DXY_PctChange_Nd"] <= self.config.max_dxy_change

        df["Signal"] = (
            cond_pullback
            & cond_wr
            & cond_reversal
            & cond_oneday_floor
            & cond_twoday_floor
            & cond_gvz
            & cond_dxy
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
            logger.info("GLD-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("GLD-016: Detected %d DXY-divergence-filtered MR signals", signal_count)
        return df

"""
TLT MOVE Implied-Vol Forward-Looking Regime-Gated MR 訊號偵測器 (TLT-013)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ≥ 3% 且 ≤ 7%
2. Williams %R(10) ≤ -80
3. 收盤位置 ≥ 40%（日內反轉）
4. BB(20, 2) 寬度 / Close < 5%（沿用 TLT-007 Att2 backward-looking realized vol gate）
5. ^MOVE 收盤值 <= max_move_level（forward-looking implied vol gate，TLT-013 核心新增）
6. （Att3 選用）^MOVE 5 日變化 <= 0（regime 改善方向過濾）
7. 冷卻期 7 天
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_013_move_implied_vol_mr.config import TLT013Config

logger = logging.getLogger(__name__)


class TLT013SignalDetector(BaseSignalDetector):
    """TLT-013：BB-width regime gate + ^MOVE forward-looking implied vol gate"""

    def __init__(self, config: TLT013Config):
        self.config = config

    def _fetch_move_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.move_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.move_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # BB-width regime gate（沿用 TLT-007 Att2）
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        # 60 日高點 drawdown（用於 Att3 prior-DD 過濾，TQQQ-018 cross-asset port）
        dd_window = self.config.prior_dd_window
        df["DD_High_N"] = df["Close"].rolling(dd_window).max()
        df["Drawdown_N"] = (df["Close"] - df["DD_High_N"]) / df["DD_High_N"]
        df["Prior_DD"] = df["Drawdown_N"].shift(self.config.prior_dd_lookback_offset)

        # ^MOVE forward-looking implied vol gate（TLT-013 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        move_df = self._fetch_move_data(start_date)

        if move_df is None or move_df.empty:
            logger.error("無法取得 %s 數據，^MOVE 過濾停用", self.config.move_ticker)
            df["MOVE_Close"] = float("nan")
            df["MOVE_Change_Nd"] = 0.0
            df["MOVE_SMA"] = float("nan")
        else:
            move_close = move_df["Close"].reindex(df.index, method="ffill")
            df["MOVE_Close"] = move_close
            df["MOVE_Change_Nd"] = move_close.diff(self.config.move_direction_lookback)
            df["MOVE_SMA"] = move_close.rolling(self.config.move_sma_window).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_bb_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio
        cond_move_level = df["MOVE_Close"] <= self.config.max_move_level

        if self.config.use_move_sma_filter:
            cond_move_sma = df["MOVE_SMA"] <= self.config.max_move_sma_level
        else:
            cond_move_sma = pd.Series(True, index=df.index)

        if self.config.use_move_direction_filter:
            cond_move_dir = df["MOVE_Change_Nd"] <= 0
        else:
            cond_move_dir = pd.Series(True, index=df.index)

        if self.config.use_prior_dd_filter:
            cond_prior_dd = df["Prior_DD"] <= self.config.max_prior_dd
        else:
            cond_prior_dd = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_bb_regime
            & cond_move_level
            & cond_move_sma
            & cond_move_dir
            & cond_prior_dd
        )

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
            logger.info("TLT-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-013: Detected %d MOVE-implied-vol-gated MR signals", signal_count)
        return df

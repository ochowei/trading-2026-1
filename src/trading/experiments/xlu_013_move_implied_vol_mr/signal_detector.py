"""
XLU-013 訊號偵測器：MOVE Implied-Vol Forward-Looking Regime-Gated MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-7%, -3.5%]（同 XLU-011 / XLU-012）
2. Williams %R(10) <= -80（同 XLU-011 / XLU-012）
3. 收盤位置 >= 40%（同 XLU-011 / XLU-012）
4. ATR(5) / ATR(20) > 1.15（同 XLU-011 / XLU-012）
5. ^MOVE 收盤值 <= max_move_level（XLU-013 核心新增 forward-looking implied vol gate）
6. （選用）^MOVE N 日變化 <= 0（regime 改善方向過濾）
7. 冷卻期 7 個交易日

跨資產移植自 TLT-013（2026-05-01 lesson #24 首次成功），測試 ^MOVE filter 在
XLU 1.08% vol 利率敏感公用事業 ETF 的有效性。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_013_move_implied_vol_mr.config import XLU013Config

logger = logging.getLogger(__name__)


class XLU013SignalDetector(BaseSignalDetector):
    """XLU-013：XLU-012 Att3 框架 + ^MOVE forward-looking implied vol gate"""

    def __init__(self, config: XLU013Config):
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

        # ATR ratio (sym to XLU-011/XLU-012)
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
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        # ^MOVE forward-looking implied vol gate（XLU-013 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        move_df = self._fetch_move_data(start_date)

        if move_df is None or move_df.empty:
            logger.error("無法取得 %s 數據，^MOVE 過濾停用", self.config.move_ticker)
            df["MOVE_Close"] = float("nan")
            df["MOVE_Change_Nd"] = 0.0
        else:
            move_close = move_df["Close"].reindex(df.index, method="ffill")
            df["MOVE_Close"] = move_close
            df["MOVE_Change_Nd"] = move_close.diff(self.config.move_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_move_level = df["MOVE_Close"] <= self.config.max_move_level

        if self.config.use_move_direction_filter:
            cond_move_dir = df["MOVE_Change_Nd"] <= 0
        else:
            cond_move_dir = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_move_level
            & cond_move_dir
        )

        # Cooldown
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
            logger.info("XLU-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("XLU-013: Detected %d MOVE-implied-vol-gated MR signals", signal_count)
        return df

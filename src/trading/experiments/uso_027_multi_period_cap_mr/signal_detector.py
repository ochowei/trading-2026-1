"""
USO-027 訊號偵測器：Multi-Period Capitulation-Strength Filter MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-12%, -7%]（沿用 USO-013/USO-025）
2. RSI(2) < 15（沿用）
3. 2 日報酬 <= -2.5%（sign-day capitulation depth, 沿用）
4. ^OVX 3 日變化 <= +4.0（沿用 USO-025 Att3 sweet spot）
5. 5 日報酬 >= return_5d_min（USO-027 核心新增 multi-day persistence dimension：
   不得太深，排除多日連續急跌 continuation regime 訊號）
6. 冷卻期 10 個交易日

跨資產移植自 URA-013（5d cap on RSI(2) MR）+ INDA-011（multi-period dimension
combo），測試 "multi-day persistence cap" 在 USO 2.2% vol commodity event-driven
ETF 的有效性。
"""

import logging

import numpy as np
import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_027_multi_period_cap_mr.config import USO027Config

logger = logging.getLogger(__name__)


class USO027SignalDetector(BaseSignalDetector):
    """USO-027：USO-025 Att3 框架 + 5d return cap multi-period persistence gate"""

    def __init__(self, config: USO027Config):
        self.config = config

    def _fetch_ovx_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.ovx_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.ovx_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（沿用）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)（沿用）
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日報酬 floor（沿用）
        df["Return_2d"] = df["Close"].pct_change(2)

        # USO-027 核心新增：N 日累計報酬（用於 multi-day persistence cap）
        df["Return_Nd"] = df["Close"].pct_change(self.config.return_5d_lookback)

        # ^OVX forward-looking implied vol gate（沿用 USO-025）
        start_date = df.index[0].strftime("%Y-%m-%d")
        ovx_df = self._fetch_ovx_data(start_date)

        if ovx_df is None or ovx_df.empty:
            logger.error("無法取得 %s 數據，^OVX 過濾停用", self.config.ovx_ticker)
            df["OVX_Close"] = float("nan")
            df["OVX_Change_Nd"] = 0.0
        else:
            ovx_close = ovx_df["Close"].reindex(df.index, method="ffill")
            df["OVX_Close"] = ovx_close
            df["OVX_Change_Nd"] = ovx_close.diff(self.config.ovx_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold

        if self.config.use_ovx_direction_filter:
            ovx_change = df["OVX_Change_Nd"].fillna(-999.0)
            cond_ovx_dir = ovx_change <= self.config.max_ovx_change
        else:
            cond_ovx_dir = pd.Series(True, index=df.index)

        if self.config.use_return_5d_cap:
            cond_5d_cap = df["Return_Nd"] >= self.config.return_5d_min
        else:
            cond_5d_cap = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback & cond_not_crash & cond_rsi & cond_drop & cond_ovx_dir & cond_5d_cap
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
            logger.info("USO-027: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "USO-027: Detected %d signals (5d cap >= %.2f%%, ^OVX 3d <= %+.1f)",
            signal_count,
            self.config.return_5d_min * 100,
            self.config.max_ovx_change,
        )
        return df

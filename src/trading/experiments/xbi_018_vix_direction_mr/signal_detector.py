"""
XBI-018 訊號偵測器：^VIX Implied-Vol DIRECTION Regime Gate Pullback MR

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 收盤價相對 pullback_lookback 日最高價回檔在
   [pullback_upper, pullback_threshold]（同 XBI-017 Att1）
2. Williams %R(wr_period) ≤ wr_threshold（同 XBI-017 Att1）
3. ClosePos ≥ close_position_threshold（同 XBI-017 Att1）
4. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （lesson #22 vol stability gate，同 XBI-017 Att1）
5. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold
   （lesson #24 BANDS gate，同 XBI-017 Att1）
6. (VIX_Close − VIX_Close.shift(vix_direction_lookback)) <= max_vix_change
   （XBI-018 新增 lesson #24 DIRECTION CEILING：排除 VIX 急升訊號）
7. 冷卻 cooldown_days 個交易日

設計依據：lesson #24 family DIRECTION 變體（repo 首次於 XBI）。XBI-017 為
BANDS 變體（VIX level 區間），XBI-018 試驗 DIRECTION 變體（VIX 上升速率
CEILING），與 XLU-013（^MOVE 3d change）/ USO-025（^OVX 3d）同類維度。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_018_vix_direction_mr.config import XBI018Config

logger = logging.getLogger(__name__)


class XBI018VixDirectionMRDetector(BaseSignalDetector):
    """XBI-018 訊號偵測器"""

    def __init__(self, config: XBI018Config):
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

        # === 回檔幅度（同 XBI-017 Att1）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 XBI-017 Att1）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # === ClosePos（同 XBI-017 Att1）===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === ATR regime（lesson #22 vol stability gate，同 XBI-017 Att1）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === ^VIX BANDS + DIRECTION gate ===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error(
                "無法取得 %s 數據，VIX BANDS / DIRECTION 過濾停用",
                self.config.vix_ticker,
            )
            df["VIX_Close"] = float("nan")
            df["VIX_Change"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Change"] = df["VIX_Close"] - df["VIX_Close"].shift(
                self.config.vix_direction_lookback
            )

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        if self.config.use_vix_bands:
            # 排除中等 VIX 帶：通過條件為 VIX <= low OR VIX > high（同 XBI-017）
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        if self.config.use_vix_direction:
            # DIRECTION CEILING：排除 VIX 急升訊號（lookback 日 VIX 變化 > 上限）
            cond_vix_direction = df["VIX_Change"] <= self.config.max_vix_change
        else:
            cond_vix_direction = pd.Series(True, index=df.index)

        signal = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_reversal
            & cond_regime_vol
            & cond_vix_bands
            & cond_vix_direction
        )

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
            logger.info(
                "XBI-018: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-018: Detected %d VIX-direction-filtered MR signals",
            signal_count,
        )
        return df

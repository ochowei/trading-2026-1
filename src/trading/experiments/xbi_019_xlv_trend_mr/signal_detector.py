"""
XBI-019 訊號偵測器：XLV Sector Parent Trend Filter on VIX Bands MR

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 收盤價相對 pullback_lookback 日最高價回檔在
   [pullback_upper, pullback_threshold]（同 XBI-017）
2. Williams %R(wr_period) ≤ wr_threshold（同 XBI-017）
3. ClosePos ≥ close_position_threshold（同 XBI-017）
4. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)（同 XBI-017）
5. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold（同 XBI-017）
6. **XBI-019 新增**：XLV 過去 xlv_lookback 日報酬 >= min_xlv_return
   （sector parent absolute momentum direction filter）
7. 冷卻 cooldown_days 個交易日

設計依據：sector parent absolute momentum direction filter（repo 首次）。
與 XBI-018 cross-asset divergence（相對強度）正交，filter 為「XLV 自身
是否處於健康狀態」之 absolute 方向過濾。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_019_xlv_trend_mr.config import XBI019Config

logger = logging.getLogger(__name__)


class XBI019SignalDetector(BaseSignalDetector):
    """XBI-019 訊號偵測器"""

    def __init__(self, config: XBI019Config):
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

        # === 回檔幅度（同 XBI-017）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 XBI-017）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # === ClosePos（同 XBI-017）===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === ATR regime（同 XBI-017）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === ^VIX BANDS gate（同 XBI-017）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，VIX BANDS 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

        # === XBI-019 新增：XLV 自身動能方向 ===
        xlv_df = self._fetch_external(self.config.xlv_ticker, start_date)
        if xlv_df is None or xlv_df.empty:
            logger.error("無法取得 %s 數據，XLV trend filter 停用", self.config.xlv_ticker)
            df["XLV_Return"] = 0.0
        else:
            xlv_close = xlv_df["Close"].reindex(df.index, method="ffill")
            df["XLV_Return"] = xlv_close.pct_change(self.config.xlv_lookback)

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

        # === XBI-019 核心：regime-conditional XLV gate ===
        # 低 VIX 帶（<= vix_low_threshold）：biotech isolated dip，不需 XLV 確認
        # 高 VIX 帶（> vix_high_threshold）：可選加 XLV panic-prep gate（XLV 10d <= cap）
        cond_vix_low = df["VIX_Close"] <= self.config.vix_low_threshold
        cond_vix_high = df["VIX_Close"] > self.config.vix_high_threshold

        if self.config.use_xlv_panic_gate:
            cond_panic_xlv = df["XLV_Return"] <= self.config.max_xlv_return_panic
            cond_high_pass = cond_vix_high & cond_panic_xlv
        else:
            cond_high_pass = cond_vix_high

        if self.config.use_vix_bands:
            cond_vix_bands = cond_vix_low | cond_high_pass
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        # === XBI-019 Att1/Att2：XLV 自身動能方向（FLOOR）過濾，已驗證失敗 ===
        if self.config.use_xlv_trend:
            cond_xlv_trend = df["XLV_Return"] >= self.config.min_xlv_return
        else:
            cond_xlv_trend = pd.Series(True, index=df.index)

        signal = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_reversal
            & cond_regime_vol
            & cond_vix_bands
            & cond_xlv_trend
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
            logger.info("XBI-019: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-019: Detected %d signals (XLV %dd return >= %.2f%%)",
            signal_count,
            self.config.xlv_lookback,
            self.config.min_xlv_return * 100,
        )
        return df

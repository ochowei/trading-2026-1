"""
XBI-018 訊號偵測器：XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 收盤價相對 pullback_lookback 日最高價回檔在
   [pullback_upper, pullback_threshold]（同 XBI-017）
2. Williams %R(wr_period) ≤ wr_threshold（同 XBI-017）
3. ClosePos ≥ close_position_threshold（同 XBI-017）
4. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)（同 XBI-017）
5. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold（同 XBI-017）
6. **XBI-018 新增**：
   - 若 use_rs_short：XBI 過去 rs_lookback_short 日報酬 - XLV 同期報酬
     <= max_rs_excess_short
   - 若 use_rs_long：XBI 過去 rs_lookback_long 日報酬 - XLV 同期報酬
     <= max_rs_excess_long
   - 兩者皆啟用時為 AND combination（EWT-010 模式）
7. 冷卻 cooldown_days 個交易日

設計依據：lesson #20 v3 cross-asset divergence regime gate（INDA-012 / EWZ-009 /
NVDA-021 / EWT-010 直接移植）。XBI-XLV 為 sub-sector ETF vs sector parent ETF
配對，repo 首次。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_018_xbi_xlv_divergence_mr.config import XBI018Config

logger = logging.getLogger(__name__)


class XBI018SignalDetector(BaseSignalDetector):
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

        # === XBI-018 新增：XBI-XLV 相對強度（短/長 lookback 報酬差）===
        xlv_df = self._fetch_external(self.config.xlv_ticker, start_date)
        if xlv_df is None or xlv_df.empty:
            logger.error("無法取得 %s 數據，XBI-XLV RS filter 停用", self.config.xlv_ticker)
            df["RS_Excess_Short"] = 0.0
            df["RS_Excess_Long"] = 0.0
        else:
            xlv_close = xlv_df["Close"].reindex(df.index, method="ffill")
            xbi_short_ret = df["Close"].pct_change(self.config.rs_lookback_short)
            xlv_short_ret = xlv_close.pct_change(self.config.rs_lookback_short)
            df["RS_Excess_Short"] = xbi_short_ret - xlv_short_ret

            xbi_long_ret = df["Close"].pct_change(self.config.rs_lookback_long)
            xlv_long_ret = xlv_close.pct_change(self.config.rs_lookback_long)
            df["RS_Excess_Long"] = xbi_long_ret - xlv_long_ret

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
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        # === XBI-018 新增：XBI-XLV cross-asset divergence cap ===
        if self.config.use_rs_short:
            cond_rs_short = df["RS_Excess_Short"] <= self.config.max_rs_excess_short
        else:
            cond_rs_short = pd.Series(True, index=df.index)

        if self.config.use_rs_long:
            cond_rs_long = df["RS_Excess_Long"] <= self.config.max_rs_excess_long
        else:
            cond_rs_long = pd.Series(True, index=df.index)

        signal = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_reversal
            & cond_regime_vol
            & cond_vix_bands
            & cond_rs_short
            & cond_rs_long
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
            logger.info("XBI-018: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-018: Detected %d signals (rs_short=%s/%.3f, rs_long=%s/%.3f)",
            signal_count,
            self.config.use_rs_short,
            self.config.max_rs_excess_short,
            self.config.use_rs_long,
            self.config.max_rs_excess_long,
        )
        return df

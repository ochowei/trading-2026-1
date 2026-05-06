"""
XBI-017 訊號偵測器：VIX Implied-Vol Regime Bands Filter Pullback MR

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 收盤價相對 pullback_lookback 日最高價回檔在
   [pullback_upper, pullback_threshold]（同 XBI-015 Att2）
2. Williams %R(wr_period) ≤ wr_threshold（同 XBI-015 Att2）
3. ClosePos ≥ close_position_threshold（日內反轉確認，同 XBI-015 Att2）
4. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （lesson #22 vol stability gate，同 XBI-015 Att2）
5. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold
   （XBI-017 新增 BANDS gate：排除中等 VIX 帶 [vix_low, vix_high]）
6. 冷卻 cooldown_days 個交易日

設計依據：lesson #24 family BANDS 變體（repo 首次）。既往 lesson #24 跨資產
驗證皆為 LEVEL CAP 或 DIRECTION 維度；BANDS 變體針對 XBI 殘餘 SLs 集中於
中等 VIX 帶（17~22）的 U 型分布特徵。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_017_vix_bands_mr.config import XBI017Config

logger = logging.getLogger(__name__)


class XBI017VixBandsMRDetector(BaseSignalDetector):
    """XBI-017 訊號偵測器"""

    def __init__(self, config: XBI017Config):
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

        # === 回檔幅度（同 XBI-015）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 XBI-015）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # === ClosePos（同 XBI-015）===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === ATR regime（lesson #22 vol stability gate，同 XBI-015）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === ^VIX BANDS gate（XBI-017 核心新增）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，VIX BANDS 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

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
            # 排除中等 VIX 帶：通過條件為 VIX <= low OR VIX > high
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        signal = (
            cond_pullback & cond_upper & cond_wr & cond_reversal & cond_regime_vol & cond_vix_bands
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
                "XBI-017: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-017: Detected %d VIX-bands-filtered MR signals",
            signal_count,
        )
        return df

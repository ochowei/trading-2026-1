"""
FCX-015 訊號偵測器：VIX BANDS Filter on Multi-Period Direction-Filter Regime
                    BB Squeeze Breakout

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 FCX-014）
2. 收盤價 > Upper BB(20, 2.0)（同 FCX-014）
3. 收盤價 > SMA(50)（同 FCX-014）
4. SMA(20) >= 1.00 * SMA(60)（lesson #22 trend regime，同 FCX-014）
5. 訊號日 3 日累計報酬 <= max_signal_day_3d_return（lesson #19 ceiling，
   同 FCX-014 Att1）
6. **^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold**
   （FCX-015 新增 BANDS gate：排除中等 VIX 帶 [vix_low, vix_high]，
   lesson #24 BANDS 變體跨策略移植自 XBI-017）
7. 冷卻 cooldown_days 個交易日

設計依據：lesson #24 family BANDS 變體（XBI-017 首次驗證於 Pullback MR 框架，
FCX-015 為 repo 首次將 BANDS 變體移植至 BB Squeeze Breakout 框架）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_015_vix_bands_breakout.config import FCX015Config

logger = logging.getLogger(__name__)


class FCX015VixBandsBreakoutDetector(BaseSignalDetector):
    """FCX-015 訊號偵測器"""

    def __init__(self, config: FCX015Config):
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

        # === Bollinger Bands（同 FCX-014）===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 FCX-014）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（同 FCX-014，lesson #22）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === 訊號日 3 日 / 1 日累計報酬（同 FCX-014，lesson #19）===
        df["Ret_3d"] = df["Close"].pct_change(3)
        df["Ret_1d"] = df["Close"].pct_change(1)

        # === ^VIX BANDS gate（FCX-015 核心新增，lesson #24 BANDS）===
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

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )

        if self.config.max_signal_day_3d_return is not None:
            cond_3d_ceiling = df["Ret_3d"] <= self.config.max_signal_day_3d_return
        else:
            cond_3d_ceiling = pd.Series(True, index=df.index)

        mode = self.config.vix_filter_mode
        vix = df["VIX_Close"]
        low = self.config.vix_low_threshold
        high = self.config.vix_high_threshold
        if mode == "bands_exclude_mid":
            cond_vix_bands = (vix <= low) | (vix > high)
        elif mode == "floor":
            cond_vix_bands = vix > low
        elif mode == "cap":
            cond_vix_bands = vix <= high
        elif mode == "bands_keep_mid":
            cond_vix_bands = (vix > low) & (vix <= high)
        elif mode == "off":
            cond_vix_bands = pd.Series(True, index=df.index)
        else:
            raise ValueError(f"unknown vix_filter_mode: {mode}")

        signal = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_trend
            & cond_3d_ceiling
            & cond_vix_bands
        )

        df["Signal"] = signal.fillna(False)

        # 冷卻期
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
                "FCX-015: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "FCX-015: Detected %d VIX-bands-filtered breakout signals",
            signal_count,
        )
        return df

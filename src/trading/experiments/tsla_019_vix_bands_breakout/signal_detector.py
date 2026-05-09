"""
TSLA-019 訊號偵測器：^VIX BANDS Regime Gate on TSLA-017 Att3 BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 TSLA-017）
2. 收盤價 > Upper BB(20, 2.0)（同 TSLA-017）
3. 收盤價 > SMA(50)（同 TSLA-017）
4. SMA(20) >= 0.99 × SMA(60)（同 TSLA-017 Att3 buffered SMA regime）
5. TSLA 20d return - QQQ 20d return >= -0.5%（同 TSLA-017 Att3 cross-asset divergence）
6. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold
   （TSLA-019 核心新增 BANDS gate：排除中等 VIX 帶 (vix_low, vix_high]）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_019_vix_bands_breakout.config import TSLA019Config

logger = logging.getLogger(__name__)


class TSLA019VixBandsBreakoutDetector(BaseSignalDetector):
    """TSLA-019：^VIX BANDS regime gate + TSLA-017 Att3 cross-asset divergence breakout"""

    def __init__(self, config: TSLA019Config):
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

        # === Bollinger Bands（同 TSLA-017）===
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

        # === SMA 趨勢確認（同 TSLA-017）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（同 TSLA-017 Att3）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === TSLA 自身 N 日報酬（給 cross-asset divergence 用，同 TSLA-017）===
        div_n = self.config.divergence_lookback
        df["TSLA_Ret_N"] = df["Close"].pct_change(div_n)

        # === QQQ benchmark cross-asset divergence regime gate（同 TSLA-017）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        bench_df = self._fetch_external(self.config.benchmark_ticker, start_date)
        if bench_df is None or bench_df.empty:
            logger.error(
                "無法取得 %s 數據，cross-asset divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["Bench_Close"] = float("nan")
            df["Bench_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            bench_close = bench_df["Close"].reindex(df.index, method="ffill")
            df["Bench_Close"] = bench_close
            df["Bench_Ret_N"] = bench_close.pct_change(div_n)
            df["Rel_Return_N"] = df["TSLA_Ret_N"] - df["Bench_Ret_N"]

        # === ^VIX BANDS gate（TSLA-019 核心新增）===
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
        cond_divergence = df["Rel_Return_N"] >= self.config.min_relative_return

        if self.config.use_vix_bands:
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        signal = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_trend
            & cond_divergence
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
            logger.info("TSLA-019: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TSLA-019: Detected %d VIX-bands-filtered cross-asset divergence breakout signals",
            signal_count,
        )
        return df

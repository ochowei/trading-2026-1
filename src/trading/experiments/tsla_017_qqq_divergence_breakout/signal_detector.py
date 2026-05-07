"""
TSLA-017 訊號偵測器：TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮，同 TSLA-015）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌，同 TSLA-015）
3. 收盤價 > SMA(50)（趨勢向上，同 TSLA-015）
4. SMA(20) ≥ 0.99 × SMA(60)（buffered multi-week trend regime，同 TSLA-015 Att3）
5. TSLA 20d return - QQQ 20d return >= min_relative_return（TSLA-017 核心新增 cross-asset
   divergence regime gate，過濾 TSLA 嚴重落後 QQQ 的 event-driven bear regime）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_017_qqq_divergence_breakout.config import TSLA017Config

logger = logging.getLogger(__name__)


class TSLA017QQQDivergenceBreakoutDetector(BaseSignalDetector):
    """TSLA-017：TSLA-QQQ cross-asset divergence + BB Squeeze breakout"""

    def __init__(self, config: TSLA017Config):
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

        # === Bollinger Bands（同 TSLA-015）===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # BB Width 是否低於百分位門檻
        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        # 過去 N 日內是否曾擠壓
        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 TSLA-015）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（同 TSLA-015 Att3 buffered SMA）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === TSLA 自身 N 日報酬（給 cross-asset divergence 用）===
        div_n = self.config.divergence_lookback
        df["TSLA_Ret_N"] = df["Close"].pct_change(div_n)

        # === QQQ benchmark cross-asset divergence regime gate（TSLA-017 核心）===
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

        df["Signal"] = (
            cond_squeeze & cond_breakout & cond_trend & cond_regime_trend & cond_divergence
        )

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
            logger.info("TSLA-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TSLA-017: Detected %d cross-asset divergence-gated breakout signals", signal_count
        )
        return df

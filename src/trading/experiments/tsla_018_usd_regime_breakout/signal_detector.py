"""
TSLA-018 訊號偵測器：TSLA-USD(UUP) Direction Regime-Gated BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 TSLA-017 Att3）
2. 收盤價 > Upper BB(20, 2.0)（同 TSLA-017 Att3）
3. 收盤價 > SMA(50)（同 TSLA-017 Att3）
4. SMA(20) ≥ 0.99 × SMA(60)（buffered multi-week trend regime，同 TSLA-017 Att3）
5. TSLA 20d return - QQQ 20d return >= min_relative_return（沿用 TSLA-017 Att3）
6. **USD regime gate（TSLA-018 核心新增）**：
   - 若 use_usd_ceiling：UUP 20d return <= max_usd_return（強勢 USD regime 過濾）
   - 若 use_usd_divergence_floor：(TSLA 20d − UUP 20d) >= min_tsla_minus_usd
     （相對背離 FLOOR）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_018_usd_regime_breakout.config import TSLA018Config

logger = logging.getLogger(__name__)


class TSLA018USDRegimeBreakoutDetector(BaseSignalDetector):
    """TSLA-018：TSLA-QQQ divergence + USD(UUP) regime gate + BB Squeeze breakout"""

    def __init__(self, config: TSLA018Config):
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

        # === 多週期趨勢 regime（同 TSLA-017 Att3 buffered SMA）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === TSLA 自身 N 日報酬 ===
        div_n = self.config.divergence_lookback
        df["TSLA_Ret_N"] = df["Close"].pct_change(div_n)

        start_date = df.index[0].strftime("%Y-%m-%d")

        # === QQQ benchmark cross-asset divergence（沿用 TSLA-017 Att3）===
        bench_df = self._fetch_external(self.config.benchmark_ticker, start_date)
        if bench_df is None or bench_df.empty:
            logger.error(
                "無法取得 %s 數據，TSLA-QQQ divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["Bench_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            bench_close = bench_df["Close"].reindex(df.index, method="ffill")
            df["Bench_Ret_N"] = bench_close.pct_change(div_n)
            df["Rel_Return_N"] = df["TSLA_Ret_N"] - df["Bench_Ret_N"]

        # === USD (UUP) regime gate（TSLA-018 核心新增）===
        usd_n = self.config.usd_lookback
        usd_df = self._fetch_external(self.config.usd_benchmark, start_date)
        if usd_df is None or usd_df.empty:
            logger.error(
                "無法取得 %s 數據，USD regime gate 停用",
                self.config.usd_benchmark,
            )
            df["USD_Ret_N"] = 0.0
            df["TSLA_minus_USD_N"] = 0.0
        else:
            usd_close = usd_df["Close"].reindex(df.index, method="ffill")
            df["USD_Ret_N"] = usd_close.pct_change(usd_n)
            df["TSLA_minus_USD_N"] = df["TSLA_Ret_N"] - df["USD_Ret_N"]

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

        signal = cond_squeeze & cond_breakout & cond_trend & cond_regime_trend & cond_divergence

        # USD regime gate
        if self.config.use_usd_ceiling:
            signal = signal & (df["USD_Ret_N"] <= self.config.max_usd_return)
        if self.config.use_usd_divergence_floor:
            signal = signal & (df["TSLA_minus_USD_N"] >= self.config.min_tsla_minus_usd)

        df["Signal"] = signal

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
            logger.info("TSLA-018: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TSLA-018: Detected %d USD-regime-gated breakout signals", signal_count)
        return df

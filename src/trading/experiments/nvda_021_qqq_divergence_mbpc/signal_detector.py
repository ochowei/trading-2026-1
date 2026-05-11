"""
NVDA-021 訊號偵測器：NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
2. Close > SMA(sma_trend_period)
3. SMA(sma_regime_short) ≥ sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered multi-week SMA regime gate）
4. 5 日高點回檔在 [pullback_max, pullback_min]
5. RSI(rsi_period) ∈ [rsi_min, rsi_max]
6. Close > Open（多頭 K 棒確認）
7. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
8. NVDA 20 日報酬 - QQQ 20 日報酬 ≤ max_relative_return（NVDA-021 核心：
   cross-asset divergence CEILING regime gate，過濾 single-stock rally exhaustion）
9. 冷卻 cooldown_days 個交易日

設計依據：lesson #19 family v3 / lesson #26 family v2 cross-asset divergence
regime gate（CEILING 方向）。Mirror INDA-012 / EWZ-009 outperformer-mean-reversion
結構，跨**策略類型**（先前皆於 MR / BB Squeeze）首次移植至 MBPC 框架。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_021_qqq_divergence_mbpc.config import NVDA021Config

logger = logging.getLogger(__name__)


class NVDA021QQQDivergenceMBPCDetector(BaseSignalDetector):
    """NVDA-021 訊號偵測器"""

    def __init__(self, config: NVDA021Config):
        self.config = config

    @staticmethod
    def _compute_rsi(close: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.where(avg_loss > 0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

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

        # === Donchian breakout freshness（同 NVDA-013）===
        donchian = df["High"].shift(1).rolling(self.config.donchian_period).max()
        df["Donchian_Upper"] = donchian
        df["IsNewHigh"] = df["High"] > donchian
        recency = self.config.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # === SMA trend filter（同 NVDA-013）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === Multi-week SMA regime（lesson #22，同 NVDA-013）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === Pullback from recent high（同 NVDA-013）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === RSI(14)（同 NVDA-013）===
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # === ATR regime（同 NVDA-013）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === NVDA 自身 N 日報酬 ===
        div_n = self.config.divergence_lookback
        df["NVDA_Ret_N"] = df["Close"].pct_change(div_n)

        # === QQQ benchmark cross-asset divergence CEILING gate（NVDA-021 核心）===
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
            df["Rel_Return_N"] = df["NVDA_Ret_N"] - df["Bench_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        cond_pullback_min = df["Pullback"] <= self.config.pullback_min
        cond_pullback_max = df["Pullback"] >= self.config.pullback_max
        cond_rsi_min = df["RSI"] >= self.config.rsi_min
        cond_rsi_max = df["RSI"] <= self.config.rsi_max
        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        if self.config.use_divergence_filter:
            cond_divergence = df["Rel_Return_N"] <= self.config.max_relative_return
        else:
            cond_divergence = pd.Series(True, index=df.index)

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_regime_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
            & cond_regime_vol
            & cond_divergence
        )

        if self.config.bullish_close_required:
            signal = signal & (df["Close"] > df["Open"])

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
                "NVDA-021: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-021: Detected %d cross-asset-divergence-gated MBPC signals",
            signal_count,
        )
        return df

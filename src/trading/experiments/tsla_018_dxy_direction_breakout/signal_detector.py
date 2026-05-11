"""
TSLA-018 訊號偵測器：DXY 5d Direction Filter on TSLA-QQQ Divergence BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 TSLA-017）
2. 收盤價 > Upper BB(20, 2.0)（同 TSLA-017）
3. 收盤價 > SMA(50)（同 TSLA-017）
4. SMA(20) ≥ 0.99 × SMA(60)（同 TSLA-017 Att3 buffered SMA regime）
5. TSLA 20d return - QQQ 20d return >= -0.5%（同 TSLA-017 Att3 divergence floor）
6. DXY N 日變化 <= max_dxy_change（TSLA-018 核心新增 spot FX macro regime gate）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_018_dxy_direction_breakout.config import TSLA018Config

logger = logging.getLogger(__name__)


class TSLA018DXYDirectionBreakoutDetector(BaseSignalDetector):
    """TSLA-018：TSLA-017 Att3 框架 + DXY 5d direction filter"""

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

        # === TSLA 自身 N 日報酬（同 TSLA-017 Att3）===
        div_n = self.config.divergence_lookback
        df["TSLA_Ret_N"] = df["Close"].pct_change(div_n)

        # === QQQ benchmark cross-asset divergence（同 TSLA-017 Att3）===
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

        # === DXY direction filter（TSLA-018 核心）===
        dxy_df = self._fetch_external(self.config.dxy_ticker, start_date)
        if dxy_df is None or dxy_df.empty:
            logger.error("無法取得 %s 數據，DXY 過濾停用", self.config.dxy_ticker)
            df["DXY_PctChange_Nd"] = 0.0
        else:
            dxy_close = dxy_df["Close"].reindex(df.index, method="ffill")
            df["DXY_PctChange_Nd"] = dxy_close.pct_change(self.config.dxy_lookback)

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
        cond_dxy = df["DXY_PctChange_Nd"] <= self.config.max_dxy_change

        df["Signal"] = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_trend
            & cond_divergence
            & cond_dxy
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
            logger.info("TSLA-018: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TSLA-018: Detected %d DXY-direction-filtered breakout signals", signal_count)
        return df

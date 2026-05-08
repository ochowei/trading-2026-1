"""
USO-026 訊號偵測器：USO-XLE Cross-Asset Divergence Regime-Gated MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-12%, -7%]（同 USO-013）
2. RSI(2) < 15（同 USO-013）
3. 2 日報酬 <= -2.5%（同 USO-013）
4. USO 20 日報酬 - XLE 20 日報酬 >= min_relative_return
   （USO-026 核心新增 cross-asset divergence gate，過濾 crude-specific
   weakness regime）
5. 冷卻期 10 個交易日

跨資產移植自 TLT-014（2026-05-02）+ TSLA-017（2026-05-07），測試
cross-asset divergence regime gate 在 USO 商品 ETF 上的有效性。
"""

import logging

import numpy as np
import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.uso_026_xle_divergence_mr.config import USO026Config

logger = logging.getLogger(__name__)


class USO026SignalDetector(BaseSignalDetector):
    """USO-026：USO-013 框架 + USO-XLE cross-asset divergence regime gate"""

    def __init__(self, config: USO026Config):
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

        # 回檔幅度（同 USO-013）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)（同 USO-013）
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日報酬（同 USO-013）
        df["Return_2d"] = df["Close"].pct_change(2)

        # USO 自身 N 日報酬（給 cross-asset divergence 用）
        div_n = self.config.divergence_lookback
        df["USO_Ret_N"] = df["Close"].pct_change(div_n)

        start_date = df.index[0].strftime("%Y-%m-%d")

        # ^OVX forward-looking implied vol gate（USO-025 sweet spot，Att3 stacking）
        ovx_df = self._fetch_external(self.config.ovx_ticker, start_date)
        if ovx_df is None or ovx_df.empty:
            logger.error("無法取得 %s 數據，^OVX 過濾停用", self.config.ovx_ticker)
            df["OVX_Close"] = float("nan")
            df["OVX_Change_Nd"] = 0.0
        else:
            ovx_close = ovx_df["Close"].reindex(df.index, method="ffill")
            df["OVX_Close"] = ovx_close
            df["OVX_Change_Nd"] = ovx_close.diff(self.config.ovx_direction_lookback)

        # benchmark cross-asset divergence gate（USO-026 核心）
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
            df["Rel_Return_N"] = df["USO_Ret_N"] - df["Bench_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold

        if self.config.use_ovx_direction_filter:
            ovx_change = df["OVX_Change_Nd"].fillna(-999.0)
            cond_ovx_dir = ovx_change <= self.config.max_ovx_change
        else:
            cond_ovx_dir = pd.Series(True, index=df.index)

        if self.config.use_divergence_filter:
            # NaN 視為通過（fallback 為包容，避免無 benchmark 數據日全部過濾）
            rel_return = df["Rel_Return_N"].fillna(0.0)
            cond_divergence = rel_return >= self.config.min_relative_return
        else:
            cond_divergence = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback & cond_not_crash & cond_rsi & cond_drop & cond_ovx_dir & cond_divergence
        )

        # Cooldown
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
            logger.info("USO-026: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "USO-026: Detected %d cross-asset-divergence-gated MR signals",
            signal_count,
        )
        return df

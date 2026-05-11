"""
TSM-013 訊號偵測器：TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated
RS Momentum Pullback

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. TSM 20 日報酬 - SMH 20 日報酬 >= relative_strength_min（同 TSM-008 RS 觸發）
2. 5 日高點回檔在 [pullback_min, pullback_max]（同 TSM-008 / TSM-011）
3. Close > SMA(sma_trend_period)（上升趨勢確認）
4. 訊號日 5 日報酬 <= ret_5d_max（同 TSM-011 Att3 rally exhaustion 過濾）
5. 訊號日 1 日報酬 <= ret_1d_max（停用，999 視為非綁定）
6. **TSM 20 日報酬 - QQQ 20 日報酬 <= max_relative_return**（TSM-013 核心：
   cross-asset divergence CEILING regime gate，過濾 single-stock rally exhaustion）
7. 冷卻 cooldown_days 個交易日

設計依據：lesson #19 family v3 / lesson #26 family v2 cross-asset divergence
regime gate（CEILING 方向）。Mirror NVDA-021（NVDA-QQQ CEILING + MBPC）結構，
跨**框架**首次移植至 RS Momentum Pullback（先前 NVDA-021 為 MBPC、INDA-012 /
EWZ-009 為 MR / BB Squeeze）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_013_qqq_divergence_rs.config import TSM013Config

logger = logging.getLogger(__name__)


class TSM013QQQDivergenceRSDetector(BaseSignalDetector):
    """TSM-013 訊號偵測器"""

    def __init__(self, config: TSM013Config):
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

        start_date = df.index[0].strftime("%Y-%m-%d")
        smh_df = self._fetch_external(self.config.reference_ticker, start_date)
        qqq_df = self._fetch_external(self.config.benchmark_ticker, start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["Ret_1d"] = 0.0
            df["Ret_5d"] = 0.0
            df["Rel_Return_QQQ"] = 0.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        if qqq_df is not None and not qqq_df.empty:
            common_idx = common_idx.intersection(qqq_df.index)
        df = df.loc[common_idx]

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_5d"] = df["Close"].pct_change(5)

        # === TSM-QQQ Cross-Asset Divergence CEILING（TSM-013 核心）===
        div_n = self.config.divergence_lookback
        df["TSM_Ret_DivN"] = df["Close"].pct_change(div_n)
        if qqq_df is not None and not qqq_df.empty:
            qqq_close = qqq_df["Close"].reindex(df.index, method="ffill")
            df["QQQ_Close"] = qqq_close
            df["QQQ_Ret_DivN"] = qqq_close.pct_change(div_n)
            df["Rel_Return_QQQ"] = df["TSM_Ret_DivN"] - df["QQQ_Ret_DivN"]
        else:
            logger.error(
                "無法取得 %s 數據，cross-asset divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["QQQ_Close"] = float("nan")
            df["QQQ_Ret_DivN"] = 0.0
            df["Rel_Return_QQQ"] = 0.0

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_1d = df["Ret_1d"] <= self.config.ret_1d_max
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max

        if self.config.use_divergence_filter:
            cond_divergence = df["Rel_Return_QQQ"] <= self.config.max_relative_return
        else:
            cond_divergence = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_rs & cond_pullback & cond_trend & cond_1d & cond_5d & cond_divergence
        ).fillna(False)

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

        signal_count = df["Signal"].sum()
        logger.info(
            "TSM-013: Detected %d cross-asset-divergence-gated RS signals",
            signal_count,
        )
        return df

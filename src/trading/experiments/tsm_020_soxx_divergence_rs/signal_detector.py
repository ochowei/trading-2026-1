"""
TSM-020 訊號偵測器：TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated
RS Momentum Pullback

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. TSM 20 日報酬 - SMH 20 日報酬 >= relative_strength_min（同 TSM-008 RS 觸發）
2. 5 日高點回檔在 [pullback_min, pullback_max]（同 TSM-008 / TSM-011）
3. Close > SMA(sma_trend_period)（上升趨勢確認）
4. 訊號日 5 日報酬 <= ret_5d_max（同 TSM-011 Att3 rally exhaustion 過濾）
5. 訊號日 1 日報酬 <= ret_1d_max（停用，999 視為非綁定）
6. **TSM 20 日報酬 - SOXX 20 日報酬 <= max_relative_return_soxx**（TSM-020 核心：
   sector-internal cross-asset divergence CEILING regime gate，過濾 TSM 過度
   跑贏 semi-sector ETF 的 stock-specific rally exhaustion regime）
7. 冷卻 cooldown_days 個交易日

設計依據：lesson #19 family v3 / lesson #26 family v2 cross-asset divergence
regime gate（CEILING 方向）+ **lesson #20 v3 family v11 sector-internal anchor
變體**（repo 首次 sector ETF 作為 single-stock divergence anchor）。
鏡像 TSM-013 (TSM-QQQ broad-market anchor) 結構，但 anchor 改為 sector-internal
SOXX，提供 intra-sector positioning 維度。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_020_soxx_divergence_rs.config import TSM020Config

logger = logging.getLogger(__name__)


class TSM020SOXXDivergenceRSDetector(BaseSignalDetector):
    """TSM-020 訊號偵測器"""

    def __init__(self, config: TSM020Config):
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
        soxx_df = self._fetch_external(self.config.benchmark_ticker, start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["Ret_1d"] = 0.0
            df["Ret_5d"] = 0.0
            df["Rel_Return_SOXX"] = 0.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        if soxx_df is not None and not soxx_df.empty:
            common_idx = common_idx.intersection(soxx_df.index)
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

        # === TSM-SOXX Cross-Asset Divergence CEILING（TSM-020 核心）===
        div_n = self.config.divergence_lookback
        df["TSM_Ret_DivN"] = df["Close"].pct_change(div_n)
        if soxx_df is not None and not soxx_df.empty:
            soxx_close = soxx_df["Close"].reindex(df.index, method="ffill")
            df["SOXX_Close"] = soxx_close
            df["SOXX_Ret_DivN"] = soxx_close.pct_change(div_n)
            df["Rel_Return_SOXX"] = df["TSM_Ret_DivN"] - df["SOXX_Ret_DivN"]
        else:
            logger.error(
                "無法取得 %s 數據，cross-asset divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["SOXX_Close"] = float("nan")
            df["SOXX_Ret_DivN"] = 0.0
            df["Rel_Return_SOXX"] = 0.0

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
            cond_divergence = df["Rel_Return_SOXX"] <= self.config.max_relative_return_soxx
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
            "TSM-020: Detected %d sector-internal-divergence-gated RS signals",
            signal_count,
        )
        return df

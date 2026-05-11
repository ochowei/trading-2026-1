"""
TSM-019 訊號偵測器：VIX Term-Structure Regime Gate on RS Momentum Pullback

進場條件（全部滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（沿用 TSM-008 / TSM-011）
2. 5日高點回檔 3-7%
3. 收盤價 > SMA(50)
4. 5日報酬 <= +10.5%（TSM-011 Att3 rally exhaustion ceiling）
5. **^VIX3M / ^VIX <= max_vix_term_ratio**（CEILING gate）
6. **^VIX3M / ^VIX >= min_vix_term_ratio**（FLOOR gate，預設停用）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_019_vix_term_structure_rs.config import TSM019Config

logger = logging.getLogger(__name__)


class TSM019Detector(BaseSignalDetector):
    """TSM-019：VIX Term-Structure Regime Gate on RS Momentum Pullback"""

    def __init__(self, config: TSM019Config):
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
        cfg = self.config

        start_date = df.index[0].strftime("%Y-%m-%d")

        smh_df = self._fetch_external(cfg.reference_ticker, start_date)
        if smh_df is None or smh_df.empty:
            logger.error("無法取得 %s 數據，無法計算相對強度", cfg.reference_ticker)
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["Ret_1d"] = 0.0
            df["Ret_5d"] = 0.0
            df["VIX_Term_Ratio"] = 1.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        df = df.loc[common_idx]

        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        period = cfg.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = cfg.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_5d"] = df["Close"].pct_change(5)

        # === VIX term structure (^VIX3M / ^VIX) ===
        vix_df = self._fetch_external(cfg.vix_ticker, start_date)
        vix3m_df = self._fetch_external(cfg.vix3m_ticker, start_date)

        if vix_df is None or vix_df.empty or vix3m_df is None or vix3m_df.empty:
            logger.error(
                "無法取得 %s / %s 數據，VIX term structure 過濾停用",
                cfg.vix_ticker,
                cfg.vix3m_ticker,
            )
            df["VIX_Term_Ratio"] = 1.0
        else:
            vix_close = vix_df["Close"].reindex(df.index, method="ffill")
            vix3m_close = vix3m_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Close"] = vix_close
            df["VIX3M_Close"] = vix3m_close
            df["VIX_Term_Ratio"] = vix3m_close / vix_close

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_rs = df["Relative_Strength"] >= cfg.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= cfg.pullback_min) & (
            df["Pullback_5d"] <= cfg.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_1d = df["Ret_1d"] <= cfg.ret_1d_max
        cond_5d = df["Ret_5d"] <= cfg.ret_5d_max

        cond_term_ceiling = df["VIX_Term_Ratio"] <= cfg.max_vix_term_ratio
        cond_term_floor = df["VIX_Term_Ratio"] >= cfg.min_vix_term_ratio

        df["Signal"] = (
            cond_rs
            & cond_pullback
            & cond_trend
            & cond_1d
            & cond_5d
            & cond_term_ceiling
            & cond_term_floor
        )
        df["Signal"] = df["Signal"].fillna(False)

        # Cooldown suppression
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False

        signal_count = df["Signal"].sum()
        logger.info(
            "TSM-019: Detected %d VIX-term-structure-filtered signals",
            signal_count,
        )
        return df

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

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_019_vix_term_structure_rs.config import TSM019Config

logger = logging.getLogger(__name__)


class TSM019Detector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM-019：VIX Term-Structure Regime Gate on RS Momentum Pullback"""

    def __init__(self, config: TSM019Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (
            self.config.reference_ticker,
            self.config.vix_ticker,
            self.config.vix3m_ticker,
        )

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        smh_df = self.require_auxiliary(cfg.reference_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        period = cfg.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = cfg.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_5d"] = df["Close"].pct_change(5)

        # === VIX term structure (^VIX3M / ^VIX) ===
        vix_close = self.require_auxiliary(cfg.vix_ticker, df.index)["Close"]
        vix3m_close = self.require_auxiliary(cfg.vix3m_ticker, df.index)["Close"]
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

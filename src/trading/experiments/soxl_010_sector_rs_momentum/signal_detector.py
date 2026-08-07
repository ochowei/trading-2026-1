"""
SOXL-010 訊號偵測器：Semiconductor Sector RS Momentum Pullback

進場條件（全部滿足）：
1. SOXX 10日報酬 - SPY 10日報酬 >= 6%（半導體板塊相對大盤超額表現，短期動量）
2. SOXL 5日高點回撤 8-16%（短暫整理，3x 槓桿縮放）
3. SOXL 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.soxl_010_sector_rs_momentum.config import SOXLSectorRSConfig

logger = logging.getLogger(__name__)


class SOXLSectorRSDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """SOXL 半導體板塊 RS 動量回調訊號偵測器"""

    def __init__(self, config: SOXLSectorRSConfig):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.sector_ticker, self.config.benchmark_ticker)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        soxx_df = self.require_auxiliary(cfg.sector_ticker, df.index)
        spy_df = self.require_auxiliary(cfg.benchmark_ticker, df.index)

        # SMA trend on SOXL
        df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        # Sector RS: SOXX 20d return - SPY 20d return
        period = cfg.relative_strength_period
        soxx_return = soxx_df["Close"].pct_change(period)
        spy_return = spy_df["Close"].pct_change(period)
        df["Relative_Strength"] = soxx_return - spy_return

        # SOXL 5-day pullback from high
        lookback = cfg.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Semiconductor sector outperforms broad market
        cond_rs = df["Relative_Strength"] >= cfg.relative_strength_min

        # SOXL short-term pullback within range
        cond_pullback = (df["Pullback_5d"] >= cfg.pullback_min) & (
            df["Pullback_5d"] <= cfg.pullback_max
        )

        # Uptrend confirmation
        cond_trend = df["Close"] > df["SMA_Trend"]

        df["Signal"] = cond_rs & cond_pullback & cond_trend

        # Cooldown mechanism
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
        logger.info("SOXL: Detected %d sector RS momentum signals", signal_count)
        return df

"""
TSM-021 訊號偵測器：QQQ Macro-Health Gate on RS Momentum Pullback

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. TSM 20 日報酬 - SMH 20 日報酬 >= relative_strength_min
2. 5 日高點回檔在 [pullback_min, pullback_max]
3. Close > SMA(sma_trend_period)
4. 訊號日 5 日報酬 <= ret_5d_max
5. 訊號日 1 日報酬 <= ret_1d_max（停用，999 視為非綁定）
6. **QQQ macro_lookback 日報酬 >= macro_min_return**（FLOOR：broad-market 健康確認）
7. **QQQ macro_lookback 日報酬 <= macro_max_return**（CEILING：broad-market 過熱排除，
   999 視為停用）
8. 冷卻 cooldown_days 個交易日

設計依據：lesson #25 cross-strategy mirror extension（IWM-015 broad-market
context confirmation gate 的 momentum-framework 鏡像版本）。IWM-015 為 MR
框架要求 broad-market 已 confirmed risk-off (CEILING)，本實驗為 momentum
pullback 框架要求 broad-market 未進入 deep correction (FLOOR)。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_021_qqq_macro_health_gate.config import TSM021Config

logger = logging.getLogger(__name__)


class TSM021QQQMacroHealthGateDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM-021 訊號偵測器"""

    def __init__(self, config: TSM021Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker, self.config.macro_ticker)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies both references aligned as-of to every
        # primary decision session.
        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)
        qqq_df = self.require_auxiliary(self.config.macro_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_5d"] = df["Close"].pct_change(5)

        # === QQQ broad-market macro-health gate（TSM-021 核心新增）===
        qqq_close = qqq_df["Close"]
        df["QQQ_Close"] = qqq_close
        df["QQQ_Macro_Return"] = qqq_close.pct_change(self.config.macro_lookback)

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

        cond_macro_floor = df["QQQ_Macro_Return"] >= self.config.macro_min_return
        cond_macro_ceil = df["QQQ_Macro_Return"] <= self.config.macro_max_return

        df["Signal"] = (
            cond_rs
            & cond_pullback
            & cond_trend
            & cond_1d
            & cond_5d
            & cond_macro_floor
            & cond_macro_ceil
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
            "TSM-021: Detected %d macro-health-gated RS signals",
            signal_count,
        )
        return df

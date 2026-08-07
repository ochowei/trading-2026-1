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

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_020_soxx_divergence_rs.config import TSM020Config

logger = logging.getLogger(__name__)


class TSM020SOXXDivergenceRSDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM-020 訊號偵測器"""

    def __init__(self, config: TSM020Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker, self.config.benchmark_ticker)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies both references aligned as-of to every
        # primary decision session.
        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)
        soxx_df = self.require_auxiliary(self.config.benchmark_ticker, df.index)

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

        # === TSM-SOXX Cross-Asset Divergence CEILING（TSM-020 核心）===
        div_n = self.config.divergence_lookback
        df["TSM_Ret_DivN"] = df["Close"].pct_change(div_n)
        soxx_close = soxx_df["Close"]
        df["SOXX_Close"] = soxx_close
        df["SOXX_Ret_DivN"] = soxx_close.pct_change(div_n)
        df["Rel_Return_SOXX"] = df["TSM_Ret_DivN"] - df["SOXX_Ret_DivN"]

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

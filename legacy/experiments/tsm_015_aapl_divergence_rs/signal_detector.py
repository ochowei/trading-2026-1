"""
TSM-015 訊號偵測器：TSM-AAPL Cross-Asset Divergence Regime-Gated
RS Momentum Pullback

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. TSM 20 日報酬 - SMH 20 日報酬 >= relative_strength_min（同 TSM-008 RS 觸發）
2. 5 日高點回檔在 [pullback_min, pullback_max]（同 TSM-008 / TSM-011）
3. Close > SMA(sma_trend_period)（上升趨勢確認）
4. 訊號日 5 日報酬 <= ret_5d_max（同 TSM-011 Att3 rally exhaustion 過濾）
5. **TSM 20 日報酬 - AAPL 20 日報酬 >= min_relative_return_aapl**
   （TSM-015 核心：主要客戶 cross-asset divergence regime gate FLOOR）
6. （可選）TSM 20 日報酬 - QQQ 20 日報酬 <= max_relative_return_qqq（CEILING）
7. 冷卻 cooldown_days 個交易日

設計依據：repo 首次 AAPL（TSM 主要客戶）為 cross-asset divergence anchor 試驗。
平行於 TSM-013/014（QQQ broad benchmark anchor）但鎖定客戶軸線。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tsm_015_aapl_divergence_rs.config import TSM015Config

logger = logging.getLogger(__name__)


class TSM015AAPLDivergenceDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """TSM-015 訊號偵測器"""

    def __init__(self, config: TSM015Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (
            self.config.reference_ticker,
            self.config.customer_ticker,
            self.config.benchmark_ticker,
        )

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # The verified bundle supplies all references aligned as-of to every
        # primary decision session.
        smh_df = self.require_auxiliary(self.config.reference_ticker, df.index)
        aapl_df = self.require_auxiliary(self.config.customer_ticker, df.index)
        qqq_df = self.require_auxiliary(self.config.benchmark_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_5d"] = df["Close"].pct_change(5)

        # === TSM-AAPL Cross-Asset Divergence FLOOR（TSM-015 核心）===
        aapl_n = self.config.aapl_divergence_lookback
        df["TSM_Ret_AaplN"] = df["Close"].pct_change(aapl_n)
        aapl_close = aapl_df["Close"]
        df["AAPL_Close"] = aapl_close
        df["AAPL_Ret_AaplN"] = aapl_close.pct_change(aapl_n)
        df["Rel_Return_AAPL"] = df["TSM_Ret_AaplN"] - df["AAPL_Ret_AaplN"]

        # === TSM-QQQ Cross-Asset Divergence CEILING（可選）===
        qqq_n = self.config.qqq_divergence_lookback
        df["TSM_Ret_QqqN"] = df["Close"].pct_change(qqq_n)
        qqq_close = qqq_df["Close"]
        df["QQQ_Close"] = qqq_close
        df["QQQ_Ret_QqqN"] = qqq_close.pct_change(qqq_n)
        df["Rel_Return_QQQ"] = df["TSM_Ret_QqqN"] - df["QQQ_Ret_QqqN"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max

        if self.config.use_aapl_floor:
            cond_aapl_floor = df["Rel_Return_AAPL"] >= self.config.min_relative_return_aapl
        else:
            cond_aapl_floor = pd.Series(True, index=df.index)

        if self.config.use_aapl_ceiling:
            cond_aapl_ceiling = df["Rel_Return_AAPL"] <= self.config.max_relative_return_aapl
        else:
            cond_aapl_ceiling = pd.Series(True, index=df.index)

        cond_aapl = cond_aapl_floor & cond_aapl_ceiling

        if self.config.use_qqq_ceiling:
            cond_qqq = df["Rel_Return_QQQ"] <= self.config.max_relative_return_qqq
        else:
            cond_qqq = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_rs & cond_pullback & cond_trend & cond_5d & cond_aapl & cond_qqq
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
            "TSM-015: Detected %d AAPL-divergence-gated RS signals",
            signal_count,
        )
        return df

"""
EWT-011 訊號偵測器：Volatility-Regime-Gated RS Momentum Pullback

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. EWT 20日報酬 − EEM 20日報酬 >= relative_strength_min（沿用 EWT-007）
2. 5日高點回撤 ∈ [pullback_min, pullback_max]（沿用 EWT-007）
3. Close > SMA(50)（沿用 EWT-007）
4. ATR(atr_period)/Close <= max_atr_pct（EWT-011 核心新增波動率 regime 閘門）
5. 冷卻期 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.ewt_011_vol_gated_rs_momentum.config import EWT011Config

logger = logging.getLogger(__name__)


class EWT011SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """EWT Volatility-Regime-Gated RS Momentum Pullback 訊號偵測器"""

    def __init__(self, config: EWT011Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.reference_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        ref_df = self.require_auxiliary(self.config.reference_ticker, df.index)

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["EWT_Return"] = df["Close"].pct_change(period)
        df["EEM_Return"] = ref_df["Close"].pct_change(period)
        df["Relative_Strength"] = df["EWT_Return"] - df["EEM_Return"]

        sp = self.config.rs_short_period
        df["RS_Short"] = df["Close"].pct_change(sp) - ref_df["Close"].pct_change(sp)

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        # ATR(period) / Close — 波動率 regime 量度
        prev_close = df["Close"].shift(1)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_Pct"] = tr.rolling(self.config.atr_period).mean() / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]

        if self.config.use_vol_regime_gate:
            cond_vol = df["ATR_Pct"] <= self.config.max_atr_pct
        else:
            cond_vol = pd.Series(True, index=df.index)

        if self.config.use_rs_freshness:
            cond_fresh = df["RS_Short"] > self.config.rs_short_min
        else:
            cond_fresh = pd.Series(True, index=df.index)

        df["Signal"] = cond_rs & cond_pullback & cond_trend & cond_vol & cond_fresh

        # 冷卻機制
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

        logger.info(
            "EWT-011: Detected %d vol-gated RS momentum signals",
            int(df["Signal"].sum()),
        )
        return df

"""
DIA-014 訊號偵測器：DIA-IWM Cross-Asset Divergence CEILING Regime-Gated MR

在 DIA-012 Att2 五條件 MR 進場邏輯（RSI(2)<10 + 2DD>=1.5% + ClosePos>=40%
+ 1d cap>=-2.0% + 3d cap>=-7%）之上，新增第六條件：

  DIA N 日報酬 - IWM N 日報酬 <= max_rel_return（CEILING）

當 DIA 過去 N 日相對 IWM 過度強勢（rel > 閾值），訊號日的 RSI(2) 急跌更可能
為 large-cap defensive rotation 後的 broad regime-shift 熊市起點延續（如
2022-01-18 Fed hawkish pivot），而非乾淨的 V-bounce MR 機會；CEILING filter
過濾此類訊號可移除 2022-01-18 唯一 SL（relIWM_10d +4.53%，全 Part A 最高，
與贏家最高 +2.77% 距 +1.76pp）。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.dia_014_iwm_divergence_mr.config import DIA014Config

logger = logging.getLogger(__name__)


class DIA014SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """DIA-IWM Divergence CEILING Regime-Gated MR 訊號偵測器"""

    def __init__(self, config: DIA014Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.anchor_ticker,)

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)（沿用 DIA-012）
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2 日累計跌幅（沿用 DIA-012）
        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 1 日 / 3 日報酬（沿用 DIA-012）
        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_3d"] = df["Close"].pct_change(3)

        # 收盤位置（沿用 DIA-012）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === DIA-014 核心新增：DIA-IWM 相對強度（CEILING）===
        dia_n_return = df["Close"].pct_change(self.config.rel_lookback)
        anchor_df = self.require_auxiliary(self.config.anchor_ticker, df.index)
        anchor_n_return = anchor_df["Close"].pct_change(self.config.rel_lookback)
        df["Anchor_Return_N"] = anchor_n_return
        df["DIA_Return_N"] = dia_n_return
        df["Rel_Return"] = dia_n_return - anchor_n_return

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap

        # 第六條件：DIA-IWM rel return <= max_rel_return（CEILING）
        cond_rel = df["Rel_Return"] <= self.config.max_rel_return

        df["Signal"] = (
            cond_rsi & cond_decline & cond_reversal & cond_oneday_cap & cond_threeday_cap & cond_rel
        )

        # Cooldown（沿用 DIA-012）
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
            logger.info("DIA-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-014: Detected %d signals (anchor=%s, rel_lookback=%d, max_rel_return=%+.4f)",
            signal_count,
            self.config.anchor_ticker,
            self.config.rel_lookback,
            self.config.max_rel_return,
        )
        return df

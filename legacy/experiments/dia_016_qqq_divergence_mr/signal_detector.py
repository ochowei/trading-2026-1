"""
DIA-016 訊號偵測器：DIA-QQQ Cross-Asset Divergence CEILING Regime-Gated MR

在 DIA-012 Att2 五條件 MR 進場邏輯（RSI(2)<10 + 2DD>=1.5% + ClosePos>=40%
+ 1d cap>=-2.0% + 3d cap>=-7%）之上，新增第六條件：

  DIA N 日報酬 - QQQ N 日報酬 <= max_rel_return（CEILING）

DIA-014（DIA-IWM cap-segment anchor）之平行 anchor 對照：測試 DIA-QQQ
style/value-vs-growth divergence。relQQQ_10d 移除 Part A SL 2022-01-18
（+4.51%，全 Part A 最高）但 Part B 2024-08-02 winner（relQQQ_10d +4.13%）
亦 > CEILING 預期被誤過濾——驗證 IWM（cap-segment）為優於 QQQ（style）anchor。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.dia_016_qqq_divergence_mr.config import DIA016Config

logger = logging.getLogger(__name__)


class DIA016SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """DIA-QQQ Divergence CEILING Regime-Gated MR 訊號偵測器"""

    def __init__(self, config: DIA016Config):
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

        # === DIA-016 核心新增：DIA-QQQ 相對強度（CEILING）===
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

        # 第六條件：DIA-QQQ rel return <= max_rel_return（CEILING）
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
            logger.info("DIA-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-016: Detected %d signals (anchor=%s, rel_lookback=%d, max_rel_return=%+.4f)",
            signal_count,
            self.config.anchor_ticker,
            self.config.rel_lookback,
            self.config.max_rel_return,
        )
        return df

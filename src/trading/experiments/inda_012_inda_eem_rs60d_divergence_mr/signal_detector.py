"""
INDA-012 訊號偵測器：INDA-EEM RS Divergence Filter on Multi-Period Capitulation MR

在 INDA-011 Att3 的六條件 MR 進場邏輯之上，新增第七條件：
**INDA N 日報酬 - EEM N 日報酬 <= max_rs_excess**

當 INDA 過去 N 日相對 EEM 強勢（rs > 閾值），訊號日的 capitulation 訊號更可能
為 country-specific 持續性疲弱中段而非 broad EM 同步 capitulation；filter 過濾
此類訊號可移除 2022-09-16 結構性 SL（rs_60d +15.28%，唯一 > +5%）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_012_inda_eem_rs60d_divergence_mr.config import (
    INDA012Config,
)

logger = logging.getLogger(__name__)


class INDA012SignalDetector(BaseSignalDetector):
    """INDA-EEM RS Divergence-Gated Multi-Period Capitulation MR 訊號偵測器"""

    def __init__(self, config: INDA012Config):
        self.config = config

    def _fetch_eem_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.eem_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.eem_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        df["Return_2d"] = df["Close"].pct_change(2)
        df["Return_3d"] = df["Close"].pct_change(3)

        # === INDA-012 核心新增：INDA-EEM 相對強度（N 日報酬差）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        eem_df = self._fetch_eem_data(start_date)

        inda_n_return = df["Close"].pct_change(self.config.rs_lookback)
        if eem_df is None or eem_df.empty:
            logger.error("無法取得 %s 數據，RS filter 停用", self.config.eem_ticker)
            df["RS_Excess"] = 0.0
        else:
            eem_close = eem_df["Close"].reindex(df.index, method="ffill")
            eem_n_return = eem_close.pct_change(self.config.rs_lookback)
            df["RS_Excess"] = inda_n_return - eem_n_return

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_2d_floor = df["Return_2d"] <= self.config.drop_2d_floor
        cond_3d_cap = df["Return_3d"] >= self.config.drop_3d_cap
        cond_rs = df["RS_Excess"] <= self.config.max_rs_excess

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_2d_floor
            & cond_3d_cap
            & cond_rs
        )

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
            logger.info("INDA-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "INDA-012: Detected %d signals (rs_lookback=%d, max_rs_excess=%.4f)",
            signal_count,
            self.config.rs_lookback,
            self.config.max_rs_excess,
        )
        return df

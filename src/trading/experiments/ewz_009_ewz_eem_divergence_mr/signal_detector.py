"""
EWZ-009 訊號偵測器：EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR

在 EWZ-007 Att3 的六條件 MR 進場邏輯之上，新增第七條件：
**EWZ N 日報酬 - EEM N 日報酬 <= max_rel_return**

當 EWZ 過去 N 日相對 EEM 強勢（rel > 閾值），訊號日的 BB 下軌觸碰更可能為
country-specific 持續性疲弱中段而非 broad EM 同步 capitulation；filter 過濾此類
訊號可移除 2020-01-31 結構性 SL（rel_10d +3.78pp，唯一 > +2.5pp）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewz_009_ewz_eem_divergence_mr.config import EWZ009Config

logger = logging.getLogger(__name__)


class EWZ009SignalDetector(BaseSignalDetector):
    """EWZ-EEM Divergence-Gated Vol-Transition MR 訊號偵測器"""

    def __init__(self, config: EWZ009Config):
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

        # Bollinger Bands（沿用 EWZ-007）
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（沿用 EWZ-007）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R（沿用 EWZ-007）
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # Close Position（沿用 EWZ-007）
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio（沿用 EWZ-007）
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # Capitulation strength（沿用 EWZ-007，1d cap 模式）
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        # === EWZ-009 核心新增：EWZ-EEM 相對強度 ===
        start_date = df.index[0].strftime("%Y-%m-%d")
        eem_df = self._fetch_eem_data(start_date)

        ewz_n_return = df["Close"].pct_change(self.config.rel_lookback)
        if eem_df is None or eem_df.empty:
            logger.error("無法取得 %s 數據，rel filter 停用", self.config.eem_ticker)
            df["Rel_Return"] = 0.0
        else:
            eem_close = eem_df["Close"].reindex(df.index, method="ffill")
            eem_n_return = eem_close.pct_change(self.config.rel_lookback)
            df["EEM_Return"] = eem_n_return
            df["EWZ_Return_N"] = ewz_n_return
            df["Rel_Return"] = ewz_n_return - eem_n_return

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        if self.config.capitulation_mode == "2dd_floor":
            cond_cap_strength = df["Ret_2d"] <= self.config.capitulation_threshold
        elif self.config.capitulation_mode == "1d_floor":
            cond_cap_strength = df["Ret_1d"] <= self.config.capitulation_threshold
        elif self.config.capitulation_mode == "2dd_cap":
            cond_cap_strength = df["Ret_2d"] >= self.config.capitulation_threshold
        elif self.config.capitulation_mode == "1d_cap":
            cond_cap_strength = df["Ret_1d"] >= self.config.capitulation_threshold
        else:
            raise ValueError(f"Unsupported capitulation_mode: {self.config.capitulation_mode}")

        # 第七條件：EWZ-EEM rel return <= max_rel_return
        cond_rel = df["Rel_Return"] <= self.config.max_rel_return

        df["Signal"] = (
            cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr & cond_cap_strength & cond_rel
        )

        # Cooldown
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
            logger.info("EWZ-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EWZ-009: Detected %d signals (rel_lookback=%d, max_rel_return=%.4f)",
            signal_count,
            self.config.rel_lookback,
            self.config.max_rel_return,
        )
        return df

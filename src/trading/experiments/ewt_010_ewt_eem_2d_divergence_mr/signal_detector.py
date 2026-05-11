"""
EWT-010 訊號偵測器：EWT-EEM 雙時框 (2D) Divergence Filter on Vol-Transition MR

在 EWT-009 Att3 的六條件 MR 進場邏輯之上，新增第 7 條件：
**NOT (EWT N1 日報酬 - EEM N1 日報酬 >= short_thresh
       AND EWT N2 日報酬 - EEM N2 日報酬 >= long_thresh)**

當 EWT 同時於短期（5d）與中期（60d）皆顯著強過 EEM，訊號日的 capitulation
更可能為「Taiwan-specific 強勢中段拉回」而非「broad EM 同步 capitulation」，
filter 過濾此類 2D 結構性 outlier 訊號。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewt_010_ewt_eem_2d_divergence_mr.config import EWT010Config

logger = logging.getLogger(__name__)


class EWT010SignalDetector(BaseSignalDetector):
    """EWT-EEM 2D Divergence-Gated Vol-Transition MR 訊號偵測器"""

    def __init__(self, config: EWT010Config):
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

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10日高點回檔（崩盤隔離）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio
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

        # Capitulation strength (1日 / 2日 報酬)
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        # === EWT-010 核心新增：雙時框 EWT-EEM 相對強度 ===
        start_date = df.index[0].strftime("%Y-%m-%d")
        eem_df = self._fetch_eem_data(start_date)

        ewt_short = df["Close"].pct_change(self.config.rs_short_lookback)
        ewt_long = df["Close"].pct_change(self.config.rs_long_lookback)

        if eem_df is None or eem_df.empty:
            logger.error("無法取得 %s 數據，2D divergence filter 停用", self.config.eem_ticker)
            df["RS_Short_Excess"] = 0.0
            df["RS_Long_Excess"] = 0.0
        else:
            eem_close = eem_df["Close"].reindex(df.index, method="ffill")
            eem_short = eem_close.pct_change(self.config.rs_short_lookback)
            eem_long = eem_close.pct_change(self.config.rs_long_lookback)
            df["RS_Short_Excess"] = ewt_short - eem_short
            df["RS_Long_Excess"] = ewt_long - eem_long

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
        else:
            raise ValueError(f"Unsupported capitulation_mode: {self.config.capitulation_mode}")

        # 2D divergence filter: 過濾 (short_div >= short_thresh) AND (long_div >= long_thresh)
        cond_div_outlier = (df["RS_Short_Excess"] >= self.config.rs_short_threshold) & (
            df["RS_Long_Excess"] >= self.config.rs_long_threshold
        )
        cond_div_pass = ~cond_div_outlier

        df["Signal"] = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_closepos
            & cond_atr
            & cond_cap_strength
            & cond_div_pass
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
            logger.info("EWT-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EWT-010: Detected %d signals (short_lb=%d/thresh=%.4f, long_lb=%d/thresh=%.4f)",
            signal_count,
            self.config.rs_short_lookback,
            self.config.rs_short_threshold,
            self.config.rs_long_lookback,
            self.config.rs_long_threshold,
        )
        return df

"""
EWZ-010 訊號偵測器：EWZ–BRL Currency-Regime-Gated Vol-Transition MR

在 EWZ-009 Att1 的七條件 MR 進場邏輯之上（EWZ-007 Att3 六條件 +
EWZ–EEM 10d rel CEILING ≤ +2.5%），新增第八條件 **EWZ–BRL 貨幣 regime
gate**：
- CEILING: BRL=X N 日報酬 ≤ max_brl_return（filter 弱 BRL risk-off）
- DIVERGENCE: EWZ N 日報酬 − BRL=X N 日報酬 ≥ min_relative_return

predict→confirm 預分析判定殘餘 binding Part A SL 2019-03-25 於 BRL 各維度
皆與 9 個 Part A winners 完全交錯（無 ≥15pp robust plateau），預測
documented-failure（family v4 driver-purity 第 5 個 driver-impure
subclass：commodity-driven single-country EM equity vs own currency BRL）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewz_010_brl_regime_mr.config import EWZ010Config

logger = logging.getLogger(__name__)


class EWZ010SignalDetector(BaseSignalDetector):
    """EWZ–BRL Currency-Regime-Gated Vol-Transition MR 訊號偵測器"""

    def __init__(self, config: EWZ010Config):
        self.config = config

    def _fetch_external(self, ticker: str, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                ticker,
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
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands（沿用 EWZ-007 / EWZ-009）
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（沿用 EWZ-007 / EWZ-009）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R（沿用 EWZ-007 / EWZ-009）
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # Close Position（沿用 EWZ-007 / EWZ-009）
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio（沿用 EWZ-007 / EWZ-009）
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

        # Capitulation strength（沿用 EWZ-007 / EWZ-009，1d cap 模式）
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        start_date = df.index[0].strftime("%Y-%m-%d")

        # === 第七條件（沿用 EWZ-009 Att1）：EWZ–EEM 相對強度 ===
        eem_df = self._fetch_external(self.config.eem_ticker, start_date)
        ewz_rel_n = df["Close"].pct_change(self.config.rel_lookback)
        if eem_df is None or eem_df.empty:
            logger.error("無法取得 %s 數據，EEM rel filter 停用", self.config.eem_ticker)
            df["Rel_Return"] = 0.0
        else:
            eem_close = eem_df["Close"].reindex(df.index, method="ffill")
            df["Rel_Return"] = ewz_rel_n - eem_close.pct_change(self.config.rel_lookback)

        # === 第八條件（EWZ-010 核心新增）：EWZ–BRL 貨幣 regime gate ===
        brl_n = self.config.brl_lookback
        df["EWZ_Ret_N"] = df["Close"].pct_change(brl_n)
        brl_df = self._fetch_external(self.config.brl_ticker, start_date)
        if brl_df is None or brl_df.empty:
            logger.error(
                "無法取得 %s 數據，EWZ–BRL regime gate 停用",
                self.config.brl_ticker,
            )
            df["BRL_Ret_N"] = 0.0
            df["BRL_Rel_Return_N"] = 0.0
        else:
            brl_close = brl_df["Close"].reindex(df.index, method="ffill")
            df["BRL_Ret_N"] = brl_close.pct_change(brl_n)
            df["BRL_Rel_Return_N"] = df["EWZ_Ret_N"] - df["BRL_Ret_N"]

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

        # 第七條件（沿用 EWZ-009 Att1）：EWZ–EEM rel <= max_rel_return
        cond_rel = df["Rel_Return"] <= self.config.max_rel_return

        # 第八條件（EWZ-010 核心新增）：EWZ–BRL 貨幣 regime gate
        if self.config.use_brl_ceiling:
            cond_brl_ceiling = df["BRL_Ret_N"] <= self.config.max_brl_return
        else:
            cond_brl_ceiling = pd.Series(True, index=df.index)

        if self.config.use_brl_divergence:
            cond_brl_div = df["BRL_Rel_Return_N"] >= self.config.min_relative_return
        else:
            cond_brl_div = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_closepos
            & cond_atr
            & cond_cap_strength
            & cond_rel
            & cond_brl_ceiling
            & cond_brl_div
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
            logger.info("EWZ-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EWZ-010: Detected %d signals (brl_lookback=%d, max_brl_return=%.4f)",
            signal_count,
            self.config.brl_lookback,
            self.config.max_brl_return,
        )
        return df

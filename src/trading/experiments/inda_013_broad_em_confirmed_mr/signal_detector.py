"""
INDA-013 訊號偵測器：Broad-EM Macro-Context-Confirmed Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ∈ [pullback_cap, pullback_threshold]（沿用 inda_010）
2. WR(10) <= -80（沿用）
3. ClosePos >= 0.4（沿用）
4. ATR(5)/ATR(20) > 1.15（沿用）
5. 2 日報酬 <= -2%（沿用）
6. EEM N 日報酬 <= max_eem_return（INDA-013 核心新增 broad-EM
   macro context confirmation gate）
7. 冷卻期 cooldown_days 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_013_broad_em_confirmed_mr.config import INDA013Config

logger = logging.getLogger(__name__)


class INDA013SignalDetector(BaseSignalDetector):
    """INDA-013：inda_010 框架 + broad-EM macro context confirmation gate"""

    def __init__(self, config: INDA013Config):
        self.config = config

    def _fetch_broad_em(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.broad_em_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.broad_em_ticker)
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

        # INDA-013：broad-EM macro context (EEM N 日報酬)
        start_date = df.index[0].strftime("%Y-%m-%d")
        em_df = self._fetch_broad_em(start_date)
        if em_df is None or em_df.empty:
            logger.error("無法取得 %s，broad-EM gate 停用", self.config.broad_em_ticker)
            df["EEM_Return_N"] = -999.0
        else:
            em_close = em_df["Close"].reindex(df.index, method="ffill")
            df["EEM_Return_N"] = em_close.pct_change(self.config.eem_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_drop_floor = df["Return_2d"] <= self.config.drop_2d_floor

        if self.config.use_broad_em_gate:
            cond_em = df["EEM_Return_N"].fillna(999.0) <= self.config.max_eem_return
        else:
            cond_em = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_drop_floor
            & cond_em
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
            logger.info("INDA-013: %d signals suppressed by cooldown", len(suppressed))

        logger.info(
            "INDA-013: Detected %d signals (broad-EM macro-context-confirmed)",
            int(df["Signal"].sum()),
        )
        return df

"""
TLT HYG Credit Divergence Regime-Gated MR 訊號偵測器 (TLT-015)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 >= 3% 且 <= 7%（同 TLT-014 Att3）
2. Williams %R(10) <= -80（同 TLT-014 Att3）
3. 收盤位置 >= 40%（日內反轉，同 TLT-014 Att3）
4. BB(20, 2) 寬度 / Close < 5%（沿用 TLT-007 / TLT-013 / TLT-014 backward-looking realized vol gate）
5. ^MOVE 收盤值 <= 130（沿用 TLT-013 / TLT-014 forward-looking implied vol gate）
6. TLT 20 日報酬 - SPY 20 日報酬 >= -4%（沿用 TLT-014 Att3 cross-asset divergence gate）
7. HYG 20 日報酬 - TLT 20 日報酬 <= +5%（TLT-015 核心新增 credit divergence gate，
   過濾 credit-on regime 中 HYG 大幅跑贏 TLT 的訊號）
8. 冷卻期 7 天
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_015_hyg_credit_divergence_mr.config import TLT015Config

logger = logging.getLogger(__name__)


class TLT015SignalDetector(BaseSignalDetector):
    """TLT-015：BB-width + ^MOVE + TLT-SPY + HYG-TLT divergence regime gate MR"""

    def __init__(self, config: TLT015Config):
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

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # BB-width regime gate
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        # TLT 自身 N 日報酬
        div_n = self.config.divergence_lookback
        df["TLT_Ret_N"] = df["Close"].pct_change(div_n)

        # ^MOVE forward-looking implied vol gate
        start_date = df.index[0].strftime("%Y-%m-%d")
        move_df = self._fetch_external(self.config.move_ticker, start_date)
        if move_df is None or move_df.empty:
            logger.error("無法取得 %s 數據，^MOVE 過濾停用", self.config.move_ticker)
            df["MOVE_Close"] = float("nan")
        else:
            df["MOVE_Close"] = move_df["Close"].reindex(df.index, method="ffill")

        # SPY benchmark cross-asset divergence gate（同 TLT-014）
        bench_df = self._fetch_external(self.config.benchmark_ticker, start_date)
        if bench_df is None or bench_df.empty:
            logger.error(
                "無法取得 %s 數據，cross-asset divergence 過濾停用",
                self.config.benchmark_ticker,
            )
            df["Bench_Close"] = float("nan")
            df["Bench_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            bench_close = bench_df["Close"].reindex(df.index, method="ffill")
            df["Bench_Close"] = bench_close
            df["Bench_Ret_N"] = bench_close.pct_change(div_n)
            df["Rel_Return_N"] = df["TLT_Ret_N"] - df["Bench_Ret_N"]

        # HYG credit cross-asset divergence gate（TLT-015 核心新增）
        credit_df = self._fetch_external(self.config.credit_ticker, start_date)
        credit_n = self.config.credit_lookback
        if credit_df is None or credit_df.empty:
            logger.error(
                "無法取得 %s 數據，HYG credit divergence 過濾停用",
                self.config.credit_ticker,
            )
            df["HYG_Close"] = float("nan")
            df["HYG_Ret_N"] = 0.0
            df["Credit_Outperformance_N"] = 0.0
        else:
            hyg_close = credit_df["Close"].reindex(df.index, method="ffill")
            df["HYG_Close"] = hyg_close
            df["HYG_Ret_N"] = hyg_close.pct_change(credit_n)
            # HYG N 日報酬 - TLT N 日報酬：正值代表 HYG 跑贏 TLT（credit-on regime）
            df["Credit_Outperformance_N"] = df["HYG_Ret_N"] - df["TLT_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_bb_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio
        cond_move_level = df["MOVE_Close"] <= self.config.max_move_level
        cond_divergence = df["Rel_Return_N"] >= self.config.min_relative_return
        cond_credit = df["Credit_Outperformance_N"] <= self.config.max_credit_outperformance

        df["Signal"] = (
            cond_pullback_min
            & cond_pullback_max
            & cond_wr
            & cond_reversal
            & cond_bb_regime
            & cond_move_level
            & cond_divergence
            & cond_credit
        )

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
            logger.info("TLT-015: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-015: Detected %d HYG credit-divergence-gated MR signals", signal_count)
        return df

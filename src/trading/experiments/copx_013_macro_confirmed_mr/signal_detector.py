"""
COPX-013 訊號偵測器：Macro-Confirmed Vol-Adaptive Capitulation MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 收盤價相對 20 日最高價回檔 10-20%（同 COPX-007）
2. Williams %R(10) <= -80（超賣確認）
3. ATR(5) / ATR(20) > 1.05（波動率飆升，過濾慢磨下跌）
4. SPY N 日報酬 <= max_spy_return（lesson #25 broad-market macro gate）
5. ^VIX N 日變化 <= max_vix_change（lesson #24 forward-looking IV direction）
6. 冷卻期 12 個交易日

設計依據：lesson #24 + lesson #25 雙來源 forward-looking macro filter
- lesson #25 cross-asset port from IWM-015（broad-market context confirmation）
- lesson #24 cross-asset port from TLT-013/XLU-013/USO-025（^VIX direction）
- 跨策略：兩 lesson 既往均應用於 MR 與 BB Squeeze；首次組合於 commodity miners ETF
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_013_macro_confirmed_mr.config import COPX013Config

logger = logging.getLogger(__name__)


class COPX013SignalDetector(BaseSignalDetector):
    """COPX-013 macro-confirmed vol-adaptive capitulation MR 訊號偵測器"""

    def __init__(self, config: COPX013Config):
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

        # 回檔幅度：收盤價 vs 近 N 日最高價
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

        # ATR ratio: short-term vs long-term volatility
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

        # SPY broad-market macro context confirmation gate（lesson #25）
        start_date = df.index[0].strftime("%Y-%m-%d")
        macro_df = self._fetch_external(self.config.macro_ticker, start_date)

        if macro_df is None or macro_df.empty:
            logger.error(
                "無法取得 %s 數據，broad-market macro filter 停用",
                self.config.macro_ticker,
            )
            df["Macro_Return_Nd"] = 0.0
        else:
            macro_close = macro_df["Close"].reindex(df.index, method="ffill")
            df["Macro_Return_Nd"] = macro_close.pct_change(self.config.macro_lookback)

        # ^VIX forward-looking macro vol direction filter（lesson #24）
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error(
                "無法取得 %s 數據，VIX direction filter 停用",
                self.config.vix_ticker,
            )
            df["VIX_Change_Nd"] = 0.0
        else:
            vix_close = vix_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Change_Nd"] = vix_close.diff(self.config.vix_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_macro = df["Macro_Return_Nd"] <= self.config.max_spy_return
        cond_vix = df["VIX_Change_Nd"] <= self.config.max_vix_change

        df["Signal"] = cond_pullback & cond_upper & cond_wr & cond_vol & cond_macro & cond_vix

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
            logger.info(
                "COPX-013: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("COPX-013: Detected %d macro-confirmed MR signals", signal_count)
        return df

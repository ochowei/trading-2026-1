"""SIVR–USD Cross-Asset Divergence Regime-Gated MR 訊號偵測器 (SIVR-019)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 收盤價低於 10 日高點 7%~15%（沿用 SIVR-005 / SIVR-015 / SIVR-018）
2. Williams %R(10) ≤ -80（沿用 SIVR-005）
3. RSI(14) bullish hook：自 5 日低點回升 ≥ 3 點，且 5 日低點 ≤ 35
   （沿用 SIVR-015 Att1）
4. (Optional) ATR(5)/ATR(20) ≤ 1.20（沿用 SIVR-018 Att3，Att3 迭代關閉）
5. (Optional) Ret_3d ≤ -1.0%（沿用 SIVR-018 Att3，Att3 迭代關閉）
6. SIVR–USD cross-asset divergence regime gate（SIVR-019 核心新增）：
   - CEILING: UUP N 日報酬 ≤ max_usd_return（filter 強美元 rally regime）
   - DIVERGENCE: SIVR N 日報酬 − UUP N 日報酬 ≥ min_relative_return
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_019_usd_regime_mr.config import SIVR019Config

logger = logging.getLogger(__name__)


class SIVR019SignalDetector(BaseSignalDetector):
    """SIVR-019：SIVR-018 Att3 框架 + SIVR–USD 跨資產 divergence regime gate"""

    def __init__(self, config: SIVR019Config):
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

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        if self.config.use_rsi_hook:
            rsi_n = self.config.rsi_period
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta).where(delta < 0, 0.0)
            avg_gain = gain.rolling(rsi_n).mean()
            avg_loss = loss.rolling(rsi_n).mean()
            rs = avg_gain / avg_loss.replace(0, float("nan"))
            df["RSI"] = 100 - (100 / (1 + rs))

            hook_n = self.config.rsi_hook_lookback
            df["RSI_Min_N"] = df["RSI"].rolling(hook_n).min()
            df["RSI_Hook_Delta"] = df["RSI"] - df["RSI_Min_N"]

        if self.config.use_atr_band:
            tr = pd.concat(
                [
                    df["High"] - df["Low"],
                    (df["High"] - df["Close"].shift(1)).abs(),
                    (df["Low"] - df["Close"].shift(1)).abs(),
                ],
                axis=1,
            ).max(axis=1)
            df["ATR_Ratio"] = (
                tr.rolling(self.config.atr_short_period).mean()
                / tr.rolling(self.config.atr_long_period).mean()
            )

        if self.config.use_3d_floor:
            df["Ret_3d"] = df["Close"].pct_change(3)

        # SIVR–USD cross-asset divergence regime gate（SIVR-019 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        usd_df = self._fetch_external(self.config.usd_ticker, start_date)
        div_n = self.config.usd_lookback
        df["SIVR_Ret_N"] = df["Close"].pct_change(div_n)
        if usd_df is None or usd_df.empty:
            logger.error(
                "無法取得 %s 數據，SIVR–USD divergence 過濾停用",
                self.config.usd_ticker,
            )
            df["USD_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            usd_close = usd_df["Close"].reindex(df.index, method="ffill")
            df["USD_Ret_N"] = usd_close.pct_change(div_n)
            df["Rel_Return_N"] = df["SIVR_Ret_N"] - df["USD_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        signal = (
            (df["Pullback"] <= self.config.pullback_threshold)
            & (df["Pullback"] >= self.config.pullback_cap)
            & (df["WR"] <= self.config.wr_threshold)
        )

        if self.config.use_rsi_hook:
            signal = (
                signal
                & (df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta)
                & (df["RSI_Min_N"] <= self.config.rsi_hook_max_min)
            )

        if self.config.use_atr_band:
            signal = (
                signal
                & (df["ATR_Ratio"] >= self.config.atr_ratio_floor)
                & (df["ATR_Ratio"] <= self.config.atr_ratio_ceiling)
            )

        if self.config.use_3d_floor:
            signal = signal & (df["Ret_3d"] <= self.config.three_day_floor)

        if self.config.use_usd_ceiling:
            signal = signal & (df["USD_Ret_N"] <= self.config.max_usd_return)

        if self.config.use_usd_divergence:
            signal = signal & (df["Rel_Return_N"] >= self.config.min_relative_return)

        df["Signal"] = signal

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
                "SIVR-019: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SIVR-019: Detected %d USD-regime-gated MR signals", signal_count)
        return df

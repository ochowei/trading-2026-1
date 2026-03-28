"""
SPY-003 訊號偵測器（含 VIX 恐慌過濾）
(SPY-003 Signal Detector with VIX Fear Filter)

進場條件：10 日高點回檔 ≥2.5% + WR(10) ≤ -80 + 收盤位置 ≥40% + VIX ≥ 20，7 天冷卻。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.spy_003_optimized_wr.config import SPYVixFilterConfig

logger = logging.getLogger(__name__)


class SPYVixFilterSignalDetector(BaseSignalDetector):
    def __init__(self, config: SPYVixFilterConfig):
        self.config = config
        self._vix_data: pd.Series | None = None

    def _fetch_vix(self, start_date: str) -> pd.Series:
        """下載 VIX 收盤數據 (Fetch VIX close data)"""
        if self._vix_data is not None:
            return self._vix_data

        logger.info("SPY-003: Fetching VIX data for fear filter...")
        vix = yf.download(
            "^VIX",
            start=start_date,
            progress=False,
            auto_adjust=True,
        )
        if vix.empty:
            logger.warning("SPY-003: Failed to fetch VIX data, returning empty series")
            self._vix_data = pd.Series(dtype=float)
            return self._vix_data

        # Handle multi-level columns from yfinance
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)

        self._vix_data = vix["Close"]
        logger.info("SPY-003: VIX data fetched, %d rows", len(self._vix_data))
        return self._vix_data

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
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置 (Close Position): 0=收在最低, 1=收在最高
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # VIX 數據（合併至 SPY DataFrame）
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_close = self._fetch_vix(start_date)
        df["VIX"] = vix_close.reindex(df.index, method="ffill")

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vix = df["VIX"] >= self.config.vix_threshold

        df["Signal"] = cond_pullback & cond_wr & cond_reversal & cond_vix

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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

        signal_count = df["Signal"].sum()
        logger.info("SPY-003: Detected %d Pullback+WR+VIX signals", signal_count)
        return df

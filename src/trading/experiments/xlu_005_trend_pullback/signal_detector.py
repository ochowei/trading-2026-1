"""
XLU-005 訊號偵測器：Cross-Asset Relative Value
XLU-005 Signal Detector: Cross-Asset Relative Value (XLU vs TLT)

進場條件（全部滿足）：
1. TLT 10日報酬 > 2%（債券上漲，利率下降）
2. XLU 10日報酬 < 0.5%（XLU 尚未跟上 TLT 的漲勢）
3. XLU RSI(14) < 50（XLU 處於回檔狀態，尚未超買）
4. XLU 收盤價 > SMA(100)（長期趨勢完好）
5. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.data_fetcher import DataFetcher
from trading.experiments.xlu_005_trend_pullback.config import XLU005Config

logger = logging.getLogger(__name__)


class XLU005Detector(BaseSignalDetector):
    """XLU Cross-Asset Relative Value 訊號偵測器"""

    def __init__(self, config: XLU005Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Fetch TLT data for cross-asset signal
        start_date = df.index[0].strftime("%Y-%m-%d")
        fetcher = DataFetcher(start=start_date)
        tlt_data = fetcher.fetch_all(["TLT"])
        tlt = tlt_data["TLT"]

        # TLT N-day return
        lookback = self.config.tlt_return_lookback
        tlt_ret = tlt["Close"].pct_change(lookback)
        df["TLT_Ret"] = tlt_ret.reindex(df.index)

        # XLU N-day return
        df["XLU_Ret"] = df["Close"].pct_change(lookback)

        # RSI
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(span=self.config.rsi_period, min_periods=self.config.rsi_period).mean()
        avg_loss = loss.ewm(span=self.config.rsi_period, min_periods=self.config.rsi_period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # Long-term SMA
        df["SMA_Long"] = df["Close"].rolling(self.config.sma_long_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # TLT rallying (rates falling)
        cond_tlt_up = df["TLT_Ret"] > self.config.tlt_min_return

        # XLU lagging behind
        cond_xlu_lag = df["XLU_Ret"] < self.config.xlu_max_return

        # XLU not overbought
        cond_rsi = df["RSI"] < self.config.rsi_upper

        # XLU long-term trend intact
        cond_trend = df["Close"] > df["SMA_Long"]

        df["Signal"] = cond_tlt_up & cond_xlu_lag & cond_rsi & cond_trend

        # Cooldown mechanism
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

        signal_count = df["Signal"].sum()
        logger.info("XLU-005: Detected %d cross-asset relative value signals", signal_count)
        return df

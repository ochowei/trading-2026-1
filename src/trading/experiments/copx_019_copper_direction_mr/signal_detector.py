"""
COPX-019 訊號偵測器: HG=F (Copper Futures) Direction Filter on Volume-Confirmed MR

進場條件 (全部滿足, 訊號日為 T, 執行模型於 T+1 開盤進場):
1. 收盤價相對 20 日最高價回檔 10-20% (沿用 COPX-007)
2. Williams %R(10) <= -80 (沿用 COPX-007)
3. ATR(5) / ATR(20) > 1.05 (沿用 COPX-007 Att3 vol-adaptive)
4. Volume Z-score(60d) >= 0.5 (沿用 COPX-018 Att3)
5. **(COPX-019 新增) HG=F (Copper Futures) direction filter**, 三模式擇一:
   - return_floor: HG=F N 日報酬 >= min_copper_return (default -0.05)
   - return_ceil:  HG=F N 日報酬 <= max_copper_return
   - level_floor:  HG=F Close / SMA(60) >= level_floor
6. 冷卻期 12 個交易日 (沿用 COPX-018)
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_019_copper_direction_mr.config import COPX019Config

logger = logging.getLogger(__name__)


class COPX019SignalDetector(BaseSignalDetector):
    """COPX-019: vol-adaptive MR + volume-surge + HG=F direction regime gate"""

    def __init__(self, config: COPX019Config):
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
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

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
        df["ATR_Ratio"] = atr_short / atr_long

        # Volume z-score 60d (COPX-018 Att3)
        v_sma60 = df["Volume"].rolling(self.config.volume_zscore_period).mean()
        v_std60 = df["Volume"].rolling(self.config.volume_zscore_period).std()
        df["Vol_Zscore_60"] = (df["Volume"] - v_sma60) / v_std60.where(v_std60 > 0, float("nan"))

        # COPX-019 核心: HG=F (Copper Futures) direction
        start_date = df.index[0].strftime("%Y-%m-%d")
        copper_df = self._fetch_external(self.config.copper_ticker, start_date)
        if copper_df is None or copper_df.empty:
            logger.error(
                "無法取得 %s 數據, copper direction 過濾停用",
                self.config.copper_ticker,
            )
            df["Copper_Close"] = float("nan")
            df["Copper_Ret_N"] = 0.0
            df["Copper_SMA_Ratio"] = 1.0
        else:
            copper_close = copper_df["Close"].reindex(df.index, method="ffill")
            df["Copper_Close"] = copper_close
            df["Copper_Ret_N"] = copper_close.pct_change(self.config.copper_lookback)
            copper_sma = copper_close.rolling(self.config.copper_sma_period).mean()
            df["Copper_SMA_Ratio"] = copper_close / copper_sma.where(copper_sma > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_volume = df["Vol_Zscore_60"] >= self.config.volume_zscore_threshold

        mode = self.config.copper_filter_mode
        if mode == "return_floor":
            cond_copper = df["Copper_Ret_N"] >= self.config.min_copper_return
        elif mode == "return_ceil":
            cond_copper = df["Copper_Ret_N"] <= self.config.max_copper_return
        elif mode == "level_floor":
            cond_copper = df["Copper_SMA_Ratio"] >= self.config.copper_level_floor
        else:
            raise ValueError(f"Unknown copper_filter_mode: {mode}")

        signal = (
            cond_pullback
            & cond_upper
            & cond_wr
            & cond_atr
            & cond_volume.fillna(False)
            & cond_copper.fillna(False)
        )

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
            logger.info("COPX-019: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-019: Detected %d copper-direction-gated MR signals (mode=%s)",
            signal_count,
            mode,
        )
        return df

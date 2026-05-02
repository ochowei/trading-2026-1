"""
NVDA-014 訊號偵測器：Negative Relative Strength Mean Reversion (Pairs MR vs SMH)

進場條件（Att2，全部滿足）：
1. NVDA 20日報酬 - SMH 20日報酬 ≤ -3%（NVDA 相對板塊弱勢 ≥ 3pp）
2. 10日高點回檔 ≥ 6%（深回檔，capitulation 確認）
3. ATR(20) ≤ 1.40 × ATR(60)（避免極端波動爆發）
4. SMA(20) ≥ 1.00 × SMA(60)（趨勢 regime gate，lesson #22；Att2 新增）
5. 冷卻期 12 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_014_negative_rs_mr.config import NVDA014Config

logger = logging.getLogger(__name__)


class NVDA014Detector(BaseSignalDetector):
    """NVDA Negative Relative Strength Mean Reversion 訊號偵測器"""

    def __init__(self, config: NVDA014Config):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
        """下載參考標的（SMH）數據"""
        try:
            df = yf.download(
                self.config.reference_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.reference_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        start_date = df.index[0].strftime("%Y-%m-%d")
        smh_df = self._fetch_reference_data(start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback"] = 0.0
            df["ATR_Ratio"] = 1.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        df = df.loc[common_idx]

        # 相對強度 = NVDA 20d return - SMH 20d return
        period = self.config.relative_strength_period
        df["NVDA_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = df["NVDA_Return"] - df["SMH_Return"]

        # 回檔（10日高點）
        lookback = self.config.pullback_lookback
        df["High_Lookback"] = df["High"].rolling(lookback).max()
        df["Pullback"] = (df["High_Lookback"] - df["Close"]) / df["High_Lookback"]

        # ATR ratio: ATR(20) / ATR(60)
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift(1)).abs()
        low_close = (df["Low"] - df["Close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr_short = true_range.rolling(self.config.atr_regime_short).mean()
        atr_long = true_range.rolling(self.config.atr_regime_long).mean()
        df["ATR_Ratio"] = atr_short / atr_long

        # SMA regime: SMA(20) / SMA(60)（lesson #22，Att2 新增）
        sma_short = df["Close"].rolling(self.config.sma_regime_short).mean()
        sma_long = df["Close"].rolling(self.config.sma_regime_long).mean()
        df["SMA_Ratio"] = sma_short / sma_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. 負向相對強度（NVDA 跑輸 SMH）
        cond_rs = df["Relative_Strength"] <= self.config.relative_strength_max

        # 2. 深回檔
        cond_pullback = df["Pullback"] >= self.config.pullback_min

        # 3. 波動 regime gate
        cond_vol = df["ATR_Ratio"] <= self.config.vol_regime_max_ratio

        signal = cond_rs & cond_pullback & cond_vol

        # 4. 趨勢 regime gate（lesson #22，Att2 新增）
        if self.config.use_sma_regime:
            signal = signal & (df["SMA_Ratio"] >= self.config.sma_regime_ratio_min)

        df["Signal"] = signal

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

        signal_count = df["Signal"].sum()
        logger.info("NVDA-014: Detected %d negative-RS pairs MR signals", signal_count)
        return df

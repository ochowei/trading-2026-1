"""
TLT Duration-Spread Mean Reversion 訊號偵測器 (TLT-008)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. TLT lookback 日報酬 - IEF lookback 日報酬 <= relative_underperf_threshold
2. TLT 收盤位置 >= close_position_threshold（日內反轉確認）
3. TLT 今日 Close > 昨日 Close（當日轉正）
4. TLT BB(20, 2) 寬度 / Close < max_bb_width_ratio（波動率 regime 閘門）
5. 冷卻期 N 天

Att3 備用（use_spread_zscore=True 時）：
1. spread_ratio = TLT.Close / IEF.Close
2. z-score = (spread_ratio - spread_ratio.rolling(window).mean()) / spread_ratio.rolling(window).std()
3. z-score <= threshold（如 -2.0，表示 TLT/IEF 比率異常偏低）
4. 收盤位置過濾、daily up、BB regime gate、cooldown 同 Att1/Att2
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_008_duration_spread_mr.config import TLT008Config

logger = logging.getLogger(__name__)


class TLT008SignalDetector(BaseSignalDetector):
    """TLT-008：TLT 相對 IEF 存續期間價差均值回歸"""

    def __init__(self, config: TLT008Config):
        self.config = config

    def _fetch_reference_data(self, start_date: str) -> pd.DataFrame | None:
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
        ref_df = self._fetch_reference_data(start_date)

        if ref_df is None or ref_df.empty:
            logger.error("無法取得 %s 數據，無法計算配對訊號", self.config.reference_ticker)
            df["Relative_Spread"] = 0.0
            df["Spread_Ratio"] = 0.0
            df["Spread_Z"] = 0.0
            df["ClosePos"] = 0.5
            df["Daily_Up"] = False
            df["BB_Width_Ratio"] = 0.0
            return df

        common_idx = df.index.intersection(ref_df.index)
        df = df.loc[common_idx]
        ref = ref_df.loc[common_idx]

        # Relative return spread: TLT.pct_change(N) - IEF.pct_change(N)
        n = self.config.relative_lookback
        df["TLT_Ret"] = df["Close"].pct_change(n)
        df["IEF_Ret"] = ref["Close"].pct_change(n)
        df["Relative_Spread"] = df["TLT_Ret"] - df["IEF_Ret"]

        # Price ratio z-score (Att3 備用)
        df["Spread_Ratio"] = df["Close"] / ref["Close"]
        w = self.config.spread_zscore_window
        mean = df["Spread_Ratio"].rolling(w).mean()
        std = df["Spread_Ratio"].rolling(w).std()
        df["Spread_Z"] = (df["Spread_Ratio"] - mean) / std.where(std > 0, float("nan"))

        # Close position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # Daily up
        df["Daily_Up"] = df["Close"] > df["Close"].shift(1)

        # BB width ratio (regime gate)
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std_bb = df["Close"].rolling(bb_n).std()
        upper = sma + bb_k * std_bb
        lower = sma - bb_k * std_bb
        df["BB_Width_Ratio"] = (upper - lower) / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if self.config.use_spread_zscore:
            cond_spread = df["Spread_Z"] <= self.config.spread_zscore_threshold
        else:
            cond_spread = df["Relative_Spread"] <= self.config.relative_underperf_threshold

        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_daily_up = (
            df["Daily_Up"] if self.config.require_daily_up else pd.Series(True, index=df.index)
        )
        cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

        df["Signal"] = cond_spread & cond_reversal & cond_daily_up & cond_regime

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
            logger.info("TLT-008: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-008: Detected %d duration-spread MR signals", signal_count)
        return df

"""
TLT Duration-Spread Mean Reversion 訊號偵測器 (TLT-008)

Att2+ 進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 >= pullback_threshold 且 <= pullback_upper（同 TLT-007）
2. Williams %R(wr_period) <= wr_threshold（超賣）
3. TLT 收盤位置 >= close_position_threshold（日內反轉）
4. TLT BB(bb_period, bb_std) 寬度 / Close < max_bb_width_ratio（regime gate）
5. TLT relative_lookback 日報酬 - IEF relative_lookback 日報酬 <= relative_underperf_threshold
   （殖利率曲線陡峭化事件；TLT-008 核心差異）
6. 冷卻期 cooldown_days 天

Att1 純 pair 模式（require_mr_framework=False）僅檢 5 + ClosePos + daily_up + BB。

Att3 備用（use_spread_zscore=True）：
改用 spread_ratio = TLT.Close/IEF.Close 相對其 spread_zscore_window 日均值的 z-score。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_008_duration_spread_mr.config import TLT008Config

logger = logging.getLogger(__name__)


class TLT008SignalDetector(BaseSignalDetector):
    """TLT-008：TLT 相對 IEF 存續期間價差均值回歸（Att2+：hybrid MR + pair filter）"""

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
            for col in [
                "Pullback",
                "WR",
                "ClosePos",
                "BB_Width_Ratio",
                "Relative_Spread",
                "Spread_Z",
                "Daily_Up",
            ]:
                df[col] = 0.0
            return df

        common_idx = df.index.intersection(ref_df.index)
        df = df.loc[common_idx]
        ref = ref_df.loc[common_idx]

        # 回檔幅度
        n_pb = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n_pb).max()
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

        # 當日轉正
        df["Daily_Up"] = df["Close"] > df["Close"].shift(1)

        # BB width ratio (regime gate)
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std_bb = df["Close"].rolling(bb_n).std()
        upper = sma + bb_k * std_bb
        lower = sma - bb_k * std_bb
        df["BB_Width_Ratio"] = (upper - lower) / df["Close"]

        # Relative return spread: TLT.pct_change(N) - IEF.pct_change(N)
        n_rs = self.config.relative_lookback
        tlt_ret = df["Close"].pct_change(n_rs)
        ief_ret = ref["Close"].pct_change(n_rs)
        df["Relative_Spread"] = tlt_ret - ief_ret

        # Spread ratio z-score (Att3 備用)
        df["Spread_Ratio"] = df["Close"] / ref["Close"]
        w = self.config.spread_zscore_window
        mean_r = df["Spread_Ratio"].rolling(w).mean()
        std_r = df["Spread_Ratio"].rolling(w).std()
        df["Spread_Z"] = (df["Spread_Ratio"] - mean_r) / std_r.where(std_r > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 配對過濾（方向由 relative_direction_bullish 控制；Att1/Att2 為 False = 弱勢方向）
        if self.config.use_spread_zscore:
            if self.config.relative_direction_bullish:
                cond_pair = df["Spread_Z"] >= self.config.spread_zscore_threshold
            else:
                cond_pair = df["Spread_Z"] <= self.config.spread_zscore_threshold
        else:
            if self.config.relative_direction_bullish:
                cond_pair = df["Relative_Spread"] >= self.config.relative_underperf_threshold
            else:
                cond_pair = df["Relative_Spread"] <= self.config.relative_underperf_threshold

        if self.config.require_mr_framework:
            # Att2+: 完整 MR 框架 + pair 過濾
            cond_pb_min = df["Pullback"] <= self.config.pullback_threshold
            cond_pb_max = df["Pullback"] >= self.config.pullback_upper
            cond_wr = df["WR"] <= self.config.wr_threshold
            cond_close = df["ClosePos"] >= self.config.close_position_threshold
            cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

            df["Signal"] = (
                cond_pb_min & cond_pb_max & cond_wr & cond_close & cond_regime & cond_pair
            )
        else:
            # Att1 純 pair 模式
            cond_close = df["ClosePos"] >= self.config.close_position_threshold
            cond_daily_up = (
                df["Daily_Up"] if self.config.require_daily_up else pd.Series(True, index=df.index)
            )
            cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

            df["Signal"] = cond_pair & cond_close & cond_daily_up & cond_regime

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

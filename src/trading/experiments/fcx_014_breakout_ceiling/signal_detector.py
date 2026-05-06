"""
FCX-014 訊號偵測器：Multi-Period Direction-Filter Regime BB Squeeze Breakout

進場條件（全部滿足）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. SMA(20) >= 1.00 × SMA(60)（多週期趨勢 regime，lesson #22 FCX-013 Att3 甜蜜點）
5. **訊號日 3 日累計報酬 <= max_signal_day_3d_return**（lesson #19 family，
   rally exhaustion filter；FCX-014 首次將 ceiling 維度移植至 BB Squeeze 框架）
6. 冷卻期 10 個交易日

設計依據：
- lesson #19 family 的 ceiling 維度（TSM-011 Att3 RS Momentum 框架首次成功）
- FCX-013 Att3 trade-level 分析：2021-04-15 SL 為唯一 3d > 12% 訊號（12.61%），
  過濾此訊號可移除 1 筆 -7.14% SL，所有 TPs（max 11.50%）保留
- 與 lesson #22 SMA regime gate 維度結構性正交（trend regime vs return magnitude）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_014_breakout_ceiling.config import FCX014Config

logger = logging.getLogger(__name__)


class FCX014BreakoutCeilingDetector(BaseSignalDetector):
    """FCX-014 訊號偵測器"""

    def __init__(self, config: FCX014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Bollinger Bands ===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        # BB Width 是否低於百分位門檻
        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        # 過去 N 日內是否曾擠壓
        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 FCX-013）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（lesson #22）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === 訊號日 3 日 / 1 日累計報酬（lesson #19 family）===
        df["Ret_3d"] = df["Close"].pct_change(3)
        df["Ret_1d"] = df["Close"].pct_change(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )

        # 訊號日 3 日累計報酬上限（lesson #19 family ceiling）
        if self.config.max_signal_day_3d_return is not None:
            cond_3d_ceiling = df["Ret_3d"] <= self.config.max_signal_day_3d_return
        else:
            cond_3d_ceiling = pd.Series(True, index=df.index)

        # 訊號日 1 日報酬上限（lesson #19 family，1d spike exhaustion）
        if self.config.max_signal_day_1d_return is not None:
            cond_1d_ceiling = df["Ret_1d"] <= self.config.max_signal_day_1d_return
        else:
            cond_1d_ceiling = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_trend
            & cond_3d_ceiling
            & cond_1d_ceiling
        )

        # 冷卻期
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
        logger.info(
            "FCX-014: Detected %d direction-filtered regime breakout signals (3d ceiling %s)",
            signal_count,
            self.config.max_signal_day_3d_return,
        )
        return df

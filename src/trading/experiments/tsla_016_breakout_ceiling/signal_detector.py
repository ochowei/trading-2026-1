"""
TSLA-016 訊號偵測器：Multi-Period Direction-Filter Regime BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. SMA(20) >= 0.99 × SMA(60)（buffered 多週期趨勢 regime，TSLA-015 Att2/Att3 甜蜜點）
5. **訊號日 3 日累計報酬 <= max_signal_day_3d_return**（lesson #19 family，
   rally exhaustion filter；本實驗首次將 ceiling 維度移植至 TSLA BB Squeeze 框架）
6. 冷卻期 10 個交易日

設計依據：
- FCX-014 Att1 提出明確跨資產假設「ceiling 維度可能適用 TSLA-015 等高 vol BB
  Squeeze 框架」，本實驗為直接驗證
- vol scaling：TSLA 3.72% / FCX 3.0% × FCX 12% threshold ≈ 15% TSLA threshold
- 與 lesson #22 SMA regime gate 維度結構性正交
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_016_breakout_ceiling.config import TSLA016Config

logger = logging.getLogger(__name__)


class TSLA016BreakoutCeilingDetector(BaseSignalDetector):
    """TSLA-016 訊號偵測器"""

    def __init__(self, config: TSLA016Config):
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

        # === SMA 趨勢確認 ===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（lesson #22）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === 多週期波動 regime（TSLA-015 Att3 ablation 確認冗餘，預設停用）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === 訊號日多週期累計報酬（lesson #19 family）===
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_3d"] = df["Close"].pct_change(3)
        df["Ret_5d"] = df["Close"].pct_change(5)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )

        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        # 訊號日 3 日累計報酬上限（lesson #19 family ceiling）
        if self.config.max_signal_day_3d_return is not None:
            cond_3d_ceiling = df["Ret_3d"] <= self.config.max_signal_day_3d_return
        else:
            cond_3d_ceiling = pd.Series(True, index=df.index)

        # 訊號日 5 日累計報酬上限（lesson #19 family，TSM-011 軸）
        if self.config.max_signal_day_5d_return is not None:
            cond_5d_ceiling = df["Ret_5d"] <= self.config.max_signal_day_5d_return
        else:
            cond_5d_ceiling = pd.Series(True, index=df.index)

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
            & cond_regime_vol
            & cond_3d_ceiling
            & cond_5d_ceiling
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
            "TSLA-016: Detected %d direction-filtered regime breakout signals "
            "(3d ceiling %s, 5d ceiling %s)",
            signal_count,
            self.config.max_signal_day_3d_return,
            self.config.max_signal_day_5d_return,
        )
        return df

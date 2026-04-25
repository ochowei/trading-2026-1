"""
TSLA-014 訊號偵測器：Post-Capitulation Vol-Transition MR

跨資產延伸 INDA-010 / EEM-014 / VGK-008 的「10 日 pullback + 2DD floor + ATR
ratio + WR」框架至 TSLA 高波動單一股票。所有參數縮放至 TSLA 3.72% 日波動。

進場條件（全部滿足）：
1. 10 日高點回檔 in [pullback_cap, pullback_threshold]（默認 [-25%, -10%]）
2. Williams %R(10) <= -80
3. 收盤位置 >= 0.35（intraday reversal）
4. ATR(5) / ATR(20) > 1.15
5. 2 日報酬 <= drop_2d_floor（默認 -5%）
6. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsla_014_vol_transition_mr.config import TSLA014Config

logger = logging.getLogger(__name__)


class TSLA014SignalDetector(BaseSignalDetector):
    def __init__(self, config: TSLA014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 10 日高點回檔
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

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio
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

        # 2 日收盤報酬
        df["Return_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_drop_floor = df["Return_2d"] <= self.config.drop_2d_floor

        df["Signal"] = (
            cond_pullback & cond_cap & cond_wr & cond_reversal & cond_vol & cond_drop_floor
        )

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
            logger.info("TSLA-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "TSLA-014: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

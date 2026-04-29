"""
EEM-014 訊號偵測器：Post-Capitulation Vol-Transition MR

核心創新（延伸自 CIBR-012 Att3）：在 EEM-012 Att3 BB 下軌+回檔上限混合進場
框架上，新增「2 日急跌上限」過濾器，排除「崩盤加速中」的進場時點。

進場條件（全部滿足）：
1. Close <= BB(20, 2.0) 下軌
2. 10 日高點回檔 >= -7%（EM 結構性崩盤隔離）
3. Williams %R(10) <= -85
4. ClosePos >= 40%
5. ATR(5)/ATR(20) > 1.10（signal-day panic）
6. 2 日收盤報酬 >= -3.0%（repo 第 2 次 2DD cap 方向驗證，過濾 in-crash entry）
7. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_014_vol_transition_mr.config import EEM014Config

logger = logging.getLogger(__name__)


class EEM014SignalDetector(BaseSignalDetector):
    def __init__(self, config: EEM014Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（崩盤隔離）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
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

        # ATR ratio（signal-day panic）
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

        # 2 日收盤報酬（in-crash entry 過濾器）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor

        df["Signal"] = cond_bb & cond_cap & cond_wr & cond_reversal & cond_vol & cond_twoday_floor

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
            logger.info("EEM-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EEM-014: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

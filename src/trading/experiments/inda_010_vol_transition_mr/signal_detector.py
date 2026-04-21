"""
INDA-010 訊號偵測器：Post-Capitulation Vol-Transition MR

Att3 最終結論（延伸自 EEM-014 Att2，非 CIBR-012 方向）：在 INDA-005 Att3
pullback+WR+ATR 框架上，將 2DD floor 自 -1.0% 加深至 -2.0%，過濾「shallow 2DD
early-in-decline / slow-melt drift」訊號。

三次迭代路徑：
- Att1：2DD cap >= -3.0%（CIBR 方向）— min 0.08（失敗，移除 TPs）
- Att2：2DD cap >= -4.0%（放寬 CIBR 方向）— min 0.17（失敗，仍無區分力）
- Att3：2DD floor <= -2.0%（EEM 方向加深）— min 0.30（+30% 勝出）

進場條件（全部滿足）：
1. 10 日高點回檔 in [-7%, -3%]
2. Williams %R(10) <= -80
3. 收盤位置 >= 40%
4. ATR(5) / ATR(20) > 1.15
5. 2 日報酬 <= -2.0%（Att3 核心創新：加深 capitulation 深度要求）
6. 冷卻期 7 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_010_vol_transition_mr.config import INDA010Config

logger = logging.getLogger(__name__)


class INDA010SignalDetector(BaseSignalDetector):
    def __init__(self, config: INDA010Config):
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

        # ATR ratio: short-term vs long-term volatility
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
        cond_drop_cap = df["Return_2d"] >= self.config.drop_2d_cap

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_drop_floor
            & cond_drop_cap
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
            logger.info("INDA-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "INDA-010: Detected %d Post-Capitulation Vol-Transition signals",
            signal_count,
        )
        return df

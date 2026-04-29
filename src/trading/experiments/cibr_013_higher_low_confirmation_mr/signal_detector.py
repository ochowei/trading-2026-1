"""
CIBR-013 Higher-Low Structural Confirmation MR 訊號偵測器（Att3）

進場條件（全部成立）：
1. Close <= BB(20, 2.0) 下軌（統計極端進場）
2. 10 日高點回檔 >= -12%（崩盤隔離）
3. Williams %R(10) <= -80
4. ClosePos >= 40%
5. ATR(5) / ATR(20) > 1.15（panic 確認）
6. Higher-Low 結構：今日 Low > min(Low[t-5..t-1])（核心創新）
7. Swing 深度：min(Low[t-5..t-1]) <= 今日 Close * (1 - 0.5%)
8. 冷卻期 8 個交易日

設計理念：
- CIBR-008 框架（BB Lower + Pullback Cap + WR + ClosePos + ATR）為 1.5-2% vol
  板塊 ETF 已驗證最優結構（min 0.39）
- CIBR-012 Att3 在 CIBR-008 上加「2DD cap >= -4.0%」過濾「in-crash acceleration」
  進場（min 0.49）
- CIBR-013 Att3 改以「Higher-Low 結構」過濾——同樣排除「續跌進場」但用多日 swing
  維度而非 2 日 close-to-close 維度。Hypothesis：BB Lower 觸及 + 今日 Low 未破
  前 5 日低點 = bullish divergence at BB lower（多日 swing 結構反轉確認）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_013_higher_low_confirmation_mr.config import CIBR013Config

logger = logging.getLogger(__name__)


class CIBR013SignalDetector(BaseSignalDetector):
    def __init__(self, config: CIBR013Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔
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

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

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

        # Higher-Low 結構：過去 N 日 Low 最小值（不含今日）
        hl_n = self.config.higher_low_lookback
        df["MinLow_PrevN"] = df["Low"].shift(1).rolling(hl_n).min()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_pullback_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_Ratio"] > self.config.atr_ratio_threshold

        # Higher-Low 結構：今日 Low > 過去 N 日 Low 最小值
        cond_higher_low = df["Low"] > df["MinLow_PrevN"]

        # Swing 深度：過去 swing low 深於今日 Close * (1 - swing_depth_min)
        cond_swing_depth = df["MinLow_PrevN"] <= df["Close"] * (1 - self.config.swing_depth_min)

        df["Signal"] = (
            cond_bb
            & cond_pullback_cap
            & cond_wr
            & cond_closepos
            & cond_atr
            & cond_higher_low
            & cond_swing_depth
        )

        if self.config.require_bullish_bar:
            df["Signal"] = df["Signal"] & (df["Close"] > df["Open"])

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
            logger.info("CIBR-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "CIBR-013: Detected %d Higher-Low Structural Confirmation signals", signal_count
        )
        return df

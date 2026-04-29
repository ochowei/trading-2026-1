"""
IWM-012 BB 下軌 + 回檔上限混合進場訊號偵測器

cross-asset port from CIBR-008 / EWJ-003 / VGK-007 / EWT-008 / EWZ-006
successful BB-lower hybrid pattern。

進場條件（全部滿足）：
1. Close <= BB(20, 2.0) 下軌（統計自適應深度進場）
2. 10日高點回檔 >= 回檔上限（崩盤隔離，pullback 不比 cap 更深）
3. Williams %R(10) <= -80（超賣確認）
4. ClosePos >= 40%（日內反轉確認）
5. ATR(5)/ATR(20) > 1.10（波動率飆升過濾，IWM-011 驗證甜蜜點）
6. 冷卻期 8 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.iwm_012_bb_lower_pullback_cap.config import IWM012Config

logger = logging.getLogger(__name__)


class IWM012SignalDetector(BaseSignalDetector):
    def __init__(self, config: IWM012Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10日高點回檔（崩盤隔離）
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
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        df["Signal"] = cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr

        # Cooldown mechanism
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
            logger.info("IWM-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("IWM-012: Detected %d BB Lower + Pullback Cap signals", signal_count)
        return df

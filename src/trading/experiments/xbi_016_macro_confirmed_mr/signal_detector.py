"""
XBI-016 訊號偵測器：Macro-Confirmed Pullback Mean Reversion

進場條件（全部滿足）：
1. 收盤價相對 pullback_lookback 日最高價回檔在 [pullback_upper, pullback_threshold]
2. Williams %R(wr_period) ≤ wr_threshold
3. ClosePos ≥ close_position_threshold（日內反轉確認）
4. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （lesson #22 cross-strategy MR：vol stability gate）
5. **Macro N 日報酬 ≤ macro_max_return**
   （lesson #25 cross-asset port：broad-market risk regime confirmation gate）
6. 冷卻 cooldown_days 個交易日

設計依據：
    XBI-015 Att2 已透過 ATR vol regime gate 過濾 vol expansion transition 期，
    殘餘 3 筆 Part A SLs（2021-05-06 / 2022-04-19 / 2023-09-21）為「事件
    驅動板塊 ETF 在 broad-market 健康/輕微回檔時的 isolated 急殺」假設待驗證。

    Macro confirmation gate 要求 broad equity index（QQQ / SPY）已進入
    confirmed correction（N 日報酬 ≤ X%），過濾「broad-market 健康但
    biotech-specific 急殺」訊號。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xbi_016_macro_confirmed_mr.config import XBI016Config

logger = logging.getLogger(__name__)


class XBI016SignalDetector(BaseSignalDetector):
    """XBI-016 訊號偵測器"""

    def __init__(self, config: XBI016Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === 回檔幅度（同 XBI-005 / XBI-015）===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 XBI-005 / XBI-015）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # === ClosePos（同 XBI-005 / XBI-015）===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === ATR regime（lesson #22 vol stability gate，同 XBI-015 Att2）===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === Macro context confirmation gate（lesson #25 cross-asset port）===
        # MACRO_Close 由 strategy.run() 合併進來
        if "MACRO_Close" in df.columns:
            df["MACRO_Return_Nd"] = (
                df["MACRO_Close"] - df["MACRO_Close"].shift(self.config.macro_lookback)
            ) / df["MACRO_Close"].shift(self.config.macro_lookback)
        else:
            logger.warning("XBI-016: MACRO_Close 欄位缺失，macro confirmation 將停用")
            df["MACRO_Return_Nd"] = pd.Series(float("-inf"), index=df.index)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        cond_macro = df["MACRO_Return_Nd"] <= self.config.macro_max_return

        signal = cond_pullback & cond_upper & cond_wr & cond_reversal & cond_regime_vol & cond_macro

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
            logger.info(
                "XBI-016: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "XBI-016: Detected %d Macro-Confirmed Pullback MR signals",
            signal_count,
        )
        return df

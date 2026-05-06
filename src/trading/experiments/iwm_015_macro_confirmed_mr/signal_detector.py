"""
IWM-015 訊號偵測器：Macro-Confirmed Capitulation MR

進場條件（全部滿足）：
1. RSI(2) < 8（IWM-013 Att3：oscillator depth 甜蜜點）
2. 2 日累計跌幅 >= 2.5%（IWM-013 baseline）
3. 收盤位置 >= 40%（日內反轉確認）
4. ATR(5) / ATR(20) > 1.1（波動率 飆升過濾）
5. **QQQ 10 日報酬 <= max_qqq_10d_return（IWM-015 新增 macro confirmation）**
6. 冷卻 cooldown_days 個交易日

設計依據：
    IWM-013 Att3 殘存兩筆 Part A SL（2021-11-26 Omicron / 2023-03-13 SVB）的
    QQQ 10d 分別為 +0.16% / -1.11%（broad market 並未確認 risk-off），對比
    winners 的 QQQ 10d 集中於 -4% ~ -12%（系統性 broad correction）。QQQ 10d
    閾值用於要求 broad market 已進入 confirmed correction regime，過濾「孤立
    小型股急殺」訊號。

    QQQ 資料於 strategy.run() 中額外抓取並合併至 IWM DataFrame。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.iwm_015_macro_confirmed_mr.config import IWM015Config

logger = logging.getLogger(__name__)


class IWM015SignalDetector(BaseSignalDetector):
    def __init__(self, config: IWM015Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # IWM-013 Att3 base 指標
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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
        df["ATR_Ratio"] = atr_short / atr_long

        # IWM-015 新增：QQQ N 日報酬（QQQ_Close 由 strategy.run() 合併進來）
        if "QQQ_Close" in df.columns:
            df["QQQ_Return_Nd"] = (
                df["QQQ_Close"] - df["QQQ_Close"].shift(self.config.macro_lookback)
            ) / df["QQQ_Close"].shift(self.config.macro_lookback)
        else:
            logger.warning("IWM-015: QQQ_Close 欄位缺失，macro confirmation 將停用")
            df["QQQ_Return_Nd"] = pd.Series(float("-inf"), index=df.index)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_macro = df["QQQ_Return_Nd"] <= self.config.macro_max_return

        df["Signal"] = (cond_rsi & cond_decline & cond_reversal & cond_vol & cond_macro).fillna(
            False
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
            logger.info("IWM-015: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "IWM-015: Detected %d Macro-Confirmed Capitulation signals",
            signal_count,
        )
        return df

"""
DIA-019 訊號偵測器：QQQ Macro-Confirmation Gate MR

核心：在 DIA-012 Att2 框架（RSI(2)<10 + 2DD≥1.5% + ClosePos≥40% +
1d cap≥-2.0% + 3d cap≥-7%）上新增 **QQQ 10 日報酬宏觀確認閘門**
（移植 IWM-015 Att1 ★ SUCCESS），要求 NASDAQ-100 已進入 confirmed
broad correction（QQQ 10d <= macro_max_return）才放行 DIA 訊號。

進場條件（全部滿足）：
1. RSI(2) < 10（極端超賣，同 DIA-012）
2. 2 日累計跌幅 >= 1.5%（同 DIA-012）
3. 收盤位置 >= 40%（日內反轉確認，同 DIA-012）
4. 1 日報酬 >= -2.0%（DIA-012 第一維度）
5. 3 日報酬 >= -7%（DIA-012 第二維度）
6. **QQQ 10 日報酬 <= macro_max_return（DIA-019 新增 macro confirmation）**
7. 冷卻 cooldown_days 個交易日

QQQ_Close 由 strategy.run() 額外抓取並合併進 DIA DataFrame
（沿用 IWM-015 / XLU-006 / TLT-009 跨資產取值模式）。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_019_qqq_macro_confirm_mr.config import DIA019Config

logger = logging.getLogger(__name__)


class DIA019SignalDetector(BaseSignalDetector):
    def __init__(self, config: DIA019Config):
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

        # ── DIA-012 base 指標 ──
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_3d"] = df["Close"].pct_change(3)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ── DIA-019 新增：QQQ N 日報酬（QQQ_Close 由 strategy.run() 合併進來）──
        if "QQQ_Close" in df.columns:
            df["QQQ_Return_Nd"] = (
                df["QQQ_Close"] - df["QQQ_Close"].shift(self.config.macro_lookback)
            ) / df["QQQ_Close"].shift(self.config.macro_lookback)
        else:
            logger.warning("DIA-019: QQQ_Close 欄位缺失，macro confirmation 將停用")
            df["QQQ_Return_Nd"] = pd.Series(float("-inf"), index=df.index)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap
        cond_macro = df["QQQ_Return_Nd"] <= self.config.macro_max_return

        df["Signal"] = (
            cond_rsi
            & cond_decline
            & cond_reversal
            & cond_oneday_cap
            & cond_threeday_cap
            & cond_macro
        ).fillna(False)

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
            logger.info("DIA-019: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-019: Detected %d QQQ Macro-Confirmed signals",
            signal_count,
        )
        return df

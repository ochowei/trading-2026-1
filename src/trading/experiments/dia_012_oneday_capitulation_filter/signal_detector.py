"""
DIA-012 訊號偵測器：Capitulation-Depth Filter MR

核心創新：在 DIA-005 RSI(2)+2DD+ClosePos 框架上新增「1 日急跌上限 + 3 日急跌
上限」雙維度過濾器，排除兩類延續性下跌：
- 1d ≤ -2%：news/policy-driven 單日深度急跌（如 Omicron 黑色星期五）
- 3d ≤ -7%：regime-shift 級別 3 日深度急跌（如 Trump 關稅週末延續）

進場條件（全部滿足）：
1. RSI(2) < 10（極端超賣，同 DIA-005）
2. 2 日累計跌幅 >= 1.5%（幅度過濾，同 DIA-005）
3. 收盤位置 >= 40%（日內反轉確認，同 DIA-005）
4. 1 日報酬 >= -2.0%（DIA-012 第一維度：排除單日深度急跌）
5. 3 日報酬 >= -7%（DIA-012 第二維度：排除 regime-shift 級別深度急跌）
6. 冷卻期 5 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_012_oneday_capitulation_filter.config import DIA012Config

logger = logging.getLogger(__name__)


class DIA012SignalDetector(BaseSignalDetector):
    def __init__(self, config: DIA012Config):
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

        # RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2 日累計跌幅
        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 1 日報酬（DIA-012 第一維度）
        df["Return_1d"] = df["Close"].pct_change(1)

        # 3 日報酬（DIA-012 第二維度）
        df["Return_3d"] = df["Close"].pct_change(3)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap

        df["Signal"] = cond_rsi & cond_decline & cond_reversal & cond_oneday_cap & cond_threeday_cap

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
            logger.info("DIA-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-012: Detected %d Capitulation-Depth Filter signals",
            signal_count,
        )
        return df

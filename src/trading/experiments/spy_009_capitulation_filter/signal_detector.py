"""
SPY-009 訊號偵測器：Signal-Day Capitulation-Strength Filter MR

核心創新：在 SPY-005 RSI(2)+2DD+ClosePos 框架上新增「1 日跌幅下限 + 3 日急跌
上限」雙維度過濾器。**1 日跌幅下限為 repo 首次方向**（DIA-012 為 1d cap 上限，
方向相反）。

進場條件（全部滿足）：
1. RSI(2) < 10（極端超賣，同 SPY-005）
2. 2 日累計跌幅 >= 1.5%（幅度過濾，同 SPY-005）
3. 收盤位置 >= 40%（日內反轉確認，同 SPY-005）
4. 1 日報酬 <= -0.5%（SPY-009 第一維度：要求訊號日具備足夠 1d capitulation）
5. 3 日報酬 >= -8%（SPY-009 第二維度：排除 regime-shift 級別 3 日延續下跌）
6. 冷卻期 5 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.spy_009_capitulation_filter.config import SPY009Config

logger = logging.getLogger(__name__)


class SPY009SignalDetector(BaseSignalDetector):
    def __init__(self, config: SPY009Config):
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

        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_3d"] = df["Close"].pct_change(3)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        # 1 日 floor：訊號日跌幅必須 ≤ floor（更深於下限）
        cond_oneday_floor = df["Return_1d"] <= self.config.oneday_return_floor
        # 3 日 cap：3 日跌幅必須 ≥ cap（不可深於上限）
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap

        df["Signal"] = (
            cond_rsi & cond_decline & cond_reversal & cond_oneday_floor & cond_threeday_cap
        )

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
            logger.info("SPY-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "SPY-009: Detected %d Signal-Day Capitulation-Strength Filter signals",
            signal_count,
        )
        return df

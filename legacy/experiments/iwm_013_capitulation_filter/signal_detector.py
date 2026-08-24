"""
IWM-013 訊號偵測器：Capitulation-Depth Filter MR (Att3 final = RSI oscillator depth)

三次迭代測試 capitulation strength filter 的不同維度（詳見 config.py 文檔）：
- Att1：1d/3d raw return cap（DIA-012 跨資產移植）— 失敗
- Att2：3d FLOOR（require 3d depth）— 失敗
- Att3 ★：RSI(2) < 8（oscillator depth）— 成功 min(A,B)† 0.59 (+13.5%)

進場條件（Att3 最終，全部滿足）：
1. RSI(2) < 8（深度 oscillator capitulation，較 IWM-011 的 < 10 加嚴 1.25x）
2. 2 日累計跌幅 >= 2.5%（幅度過濾，同 IWM-011）
3. 收盤位置 >= 40%（日內反轉確認，同 IWM-011）
4. ATR(5) / ATR(20) > 1.1（波動率飆升過濾，同 IWM-011）
5. 1 日急跌上限（cap）— Att3 停用
6. 3 日急跌上限（cap）— Att3 停用
7. 3 日急跌下限（floor）— Att3 停用
8. 冷卻期 5 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.iwm_013_capitulation_filter.config import IWM013Config

logger = logging.getLogger(__name__)


class IWM013SignalDetector(BaseSignalDetector):
    def __init__(self, config: IWM013Config):
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

        # 1 日報酬（IWM-013 第一維度）
        df["Return_1d"] = df["Close"].pct_change(1)

        # 3 日報酬（IWM-013 第二維度）
        df["Return_3d"] = df["Close"].pct_change(3)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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
        df["ATR_Ratio"] = atr_short / atr_long

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap
        # 3 日急跌下限（require depth ≤ X%）
        threeday_floor = getattr(self.config, "threeday_return_floor", 0.0)
        cond_threeday_floor = df["Return_3d"] <= threeday_floor

        df["Signal"] = (
            cond_rsi
            & cond_decline
            & cond_reversal
            & cond_vol
            & cond_oneday_cap
            & cond_threeday_cap
            & cond_threeday_floor
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
            logger.info("IWM-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "IWM-013: Detected %d Capitulation-Depth Filter signals",
            signal_count,
        )
        return df

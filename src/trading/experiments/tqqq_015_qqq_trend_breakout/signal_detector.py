"""
TQQQ-015 訊號偵測器：QQQ Momentum → Trade TQQQ
TQQQ-015 Signal Detector: QQQ Momentum Strategy

Att3: 改用動量策略（取代 BB Squeeze Breakout）
進場條件（全部基於 QQQ 數據）：
1. QQQ 10 日 ROC > momentum_threshold（強勁短期動量）
2. QQQ 收盤價 > QQQ SMA(50)（中期趨勢向上）
3. QQQ 收盤價 > QQQ SMA(200)（長期牛市確認）
4. 冷卻期 20 個交易日

交易標的：TQQQ（3x leveraged NASDAQ）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_015_qqq_trend_breakout.config import TQQQQqqBreakoutConfig

logger = logging.getLogger(__name__)


class TQQQQqqBreakoutDetector(BaseSignalDetector):
    """QQQ Momentum 訊號偵測器（訊號基於 QQQ，交易 TQQQ）"""

    def __init__(self, config: TQQQQqqBreakoutConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "QQQ_Close" not in df.columns:
            logger.warning("QQQ_Close not found, cannot compute momentum indicators")
            return df

        qqq = df["QQQ_Close"]

        # 10-day Rate of Change
        df["QQQ_ROC10"] = qqq.pct_change(periods=10) * 100

        # SMA(50) for medium-term trend
        df["QQQ_SMA50"] = qqq.rolling(50).mean()

        # SMA(200) for long-term trend (bull market filter)
        df["QQQ_SMA200"] = qqq.rolling(200).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "QQQ_Close" not in df.columns:
            df["Signal"] = False
            return df

        # 1. Strong 10-day momentum (QQQ up >5% in 10 days)
        cond_momentum = df["QQQ_ROC10"] > self.config.momentum_threshold

        # 2. Medium-term uptrend
        cond_trend50 = df["QQQ_Close"] > df["QQQ_SMA50"]

        # 3. Long-term bull market
        cond_trend200 = df["QQQ_Close"] > df["QQQ_SMA200"]

        df["Signal"] = cond_momentum & cond_trend50 & cond_trend200

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

        signal_count = df["Signal"].sum()
        logger.info("TQQQ-015: Detected %d QQQ momentum signals", signal_count)
        return df

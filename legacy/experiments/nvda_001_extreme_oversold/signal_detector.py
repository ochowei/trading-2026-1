"""
NVDA 極端超賣均值回歸訊號偵測器
NVDA Extreme Oversold Mean Reversion Signal Detector

進場條件（全部滿足）：
1. RSI(2) < 5（極端短期超賣）
2. 2日累計跌幅 >= 7%（急跌確認）
3. 冷卻期 15 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_001_extreme_oversold.config import NVDAExtremeOversoldConfig

logger = logging.getLogger(__name__)


class NVDAExtremeOversoldDetector(BaseSignalDetector):
    """NVDA 極端超賣訊號偵測器"""

    def __init__(self, config: NVDAExtremeOversoldConfig):
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

        # 1. RSI(2)
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2. 2日累計跌幅
        df["Drop_2d"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 雙重條件
        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_drop = df["Drop_2d"] <= self.config.drop_2d_threshold

        df["Signal"] = cond_rsi & cond_drop

        # 冷卻期：抑制間隔太近的訊號
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
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
        logger.info("NVDA: Detected %d extreme oversold signals", signal_count)
        return df

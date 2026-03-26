"""
TQQQ 多日動能崩潰訊號偵測模組 (TQQQ Multi-Day Momentum Collapse Signal Detector)
偵測 5 日內多數下跌、累計跌幅夠深且位於空方趨勢中的反彈機會。
Detects rebound opportunities after multi-day declines with bearish trend confirmation.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_006_momentum_collapse.config import TQQQMomentumCollapseConfig

logger = logging.getLogger(__name__)


class TQQQMomentumCollapseDetector(BaseSignalDetector):
    """
    TQQQ 多日動能崩潰訊號偵測器 (TQQQ Multi-Day Momentum Collapse Detector)

    三個條件同時成立時觸發訊號 (Signal triggers when all 3 conditions are met):
    1. 過去 N 天中下跌日 >= min_down_days
    2. N 日累計報酬 <= cumulative_drop_threshold
    3. 收盤價 < SMA(trend_sma_period)
    """

    def __init__(self, config: TQQQMomentumCollapseConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算多日崩潰訊號所需指標。"""
        df = df.copy()
        cfg = self.config

        # 日報酬與下跌日旗標 (Daily return and down-day flag)
        df["Daily_Return"] = df["Close"].pct_change()
        df["Down_Day"] = (df["Daily_Return"] < 0).astype(int)

        # N 日下跌天數與 N 日累計報酬 (N-day down count and cumulative return)
        df["Down_Days_5"] = df["Down_Day"].rolling(window=cfg.lookback_days).sum()
        df["Return_5d"] = df["Close"] / df["Close"].shift(cfg.lookback_days) - 1

        # 趨勢位置 (Trend position)
        df["SMA50"] = df["Close"].rolling(window=cfg.trend_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測多日崩潰訊號，並套用冷卻機制。"""
        df = df.copy()
        cfg = self.config

        cond_down_days = df["Down_Days_5"] >= cfg.min_down_days
        cond_collapse = df["Return_5d"] <= cfg.cumulative_drop_threshold
        cond_bearish_trend = df["Close"] < df["SMA50"]

        df["Signal"] = cond_down_days & cond_collapse & cond_bearish_trend

        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info(
                f"[TQQQMomentumCollapseDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號 "
                f"({len(suppressed)} duplicate signals suppressed by cooldown)"
            )

        signal_count = int(df["Signal"].sum())
        logger.info(
            f"[TQQQMomentumCollapseDetector] 偵測到 {signal_count} 個多日動能崩潰訊號 "
            f"({signal_count} momentum collapse signals detected)"
        )

        return df

"""
TQQQ 多日動能崩潰訊號偵測模組 (TQQQ Multi-Day Momentum Collapse Signal Detector)
偵測 TQQQ 連續多日下跌的洗盤形態。
"""

import logging
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_momentum_collapse.config import TQQQMomentumCollapseConfig

logger = logging.getLogger(__name__)


class TQQQMomentumCollapseDetector(BaseSignalDetector):
    """
    TQQQ 多日動能崩潰訊號偵測器

    三個條件同時成立時觸發訊號：
    1. 過去 5 天中 >= 4 天收盤下跌
    2. 5 日累計報酬 <= -12%
    3. 收盤價 < 50 日 SMA
    """

    def __init__(self, config: TQQQMomentumCollapseConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算指標"""
        df = df.copy()
        cfg = self.config

        # 1. 每日報酬 (Daily return)
        df["Daily_Return"] = df["Close"].pct_change()

        # 2. 是否為下跌日 (Is down day)
        df["Is_Down"] = (df["Daily_Return"] < 0).astype(int)

        # 3. 過去 N 天的下跌日總數 (Number of down days in the last N days)
        df["Down_Days_Count"] = df["Is_Down"].rolling(window=cfg.momentum_lookback).sum()

        # 4. 過去 N 天的累計報酬 (Cumulative return over the last N days)
        # 簡單算法: (Close / Close 5天前) - 1
        df["Cum_Return_N"] = (df["Close"] / df["Close"].shift(cfg.momentum_lookback)) - 1.0

        # 5. SMA 50
        df["SMA50"] = df["Close"].rolling(window=cfg.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測多日動能崩潰訊號"""
        df = df.copy()
        cfg = self.config

        # 條件 1: 過去 N 天中 >= negative_days_threshold 天下跌
        cond1 = df["Down_Days_Count"] >= cfg.negative_days_threshold

        # 條件 2: 5 日累計報酬 <= return_threshold
        cond2 = df["Cum_Return_N"] <= cfg.return_threshold

        # 條件 3: 收盤價 < SMA 50 (確認在下降趨勢中)
        cond3 = df["Close"] < df["SMA50"]

        df["Signal"] = cond1 & cond2 & cond3

        # 冷卻機制：同一波跌勢中 N 個交易日內僅取第一個訊號
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

        signal_count = df["Signal"].sum()
        logger.info(
            f"[TQQQMomentumCollapseDetector] 偵測到 {signal_count} 個多日動能崩潰訊號 "
            f"({signal_count} momentum collapse signals detected)"
        )

        return df

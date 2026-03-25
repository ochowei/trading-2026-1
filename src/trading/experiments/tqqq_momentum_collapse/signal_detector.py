"""
TQQQ 多日動能崩潰訊號偵測模組 (TQQQ Multi-Day Momentum Collapse Signal Detector)
負責計算相關指標並產生多日動能崩潰進場訊號。
Calculates indicators and generates multi-day momentum collapse entry signals.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_momentum_collapse.config import TQQQMomentumCollapseConfig

logger = logging.getLogger(__name__)


class TQQQMomentumCollapseDetector(BaseSignalDetector):
    """
    TQQQ 多日動能崩潰訊號偵測器 (TQQQ Multi-Day Momentum Collapse Signal Detector)

    三個條件同時成立時觸發訊號 (Signal triggers when all 3 conditions are met):
    1. 負日比例：過去 N 天中 >= M 天收盤下跌
    2. 累計跌幅：N 日累計報酬 <= threshold
    3. 趨勢位置：收盤價 < SMA(50)
    """

    def __init__(self, config: TQQQMomentumCollapseConfig):
        super().__init__()
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算指標 (Compute technical indicators)"""
        if len(df) < self.config.sma_period:
            logger.warning("資料長度不足以計算 SMA，指標可能不準確 (Insufficient data for SMA)")

        # 1. 每日跌幅判斷 (Is daily return negative?)
        daily_return = df["Close"].pct_change()
        is_negative = daily_return < 0

        # 過去 N 天下跌天數 (Number of negative days in past N days)
        df["NegativeDays"] = is_negative.rolling(window=self.config.lookback_period).sum()

        # 2. 累計跌幅 (Cumulative N-day return)
        # return = Close_today / Close_(today - N) - 1
        df["CumReturnN"] = df["Close"] / df["Close"].shift(self.config.lookback_period) - 1.0

        # 3. 趨勢位置 (Trend condition: Price < SMA)
        df["SMA"] = df["Close"].rolling(window=self.config.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測進場訊號並處理冷卻期 (Detect entry signals and apply cooldown)"""
        # 如果欄位不存在代表還沒算指標
        if "NegativeDays" not in df.columns:
            df = self.compute_indicators(df)

        df["Signal"] = False

        # 條件 1: 過去 5 天中 >= 4 天收盤下跌
        cond1 = df["NegativeDays"] >= self.config.negative_days_threshold

        # 條件 2: 5 日累計報酬 <= -12%
        cond2 = df["CumReturnN"] <= self.config.cumulative_drop_threshold

        # 條件 3: 收盤價 < 50 日 SMA
        cond3 = df["Close"] < df["SMA"]

        raw_signals = cond1 & cond2 & cond3

        # 處理冷卻期 (Apply cooldown)
        cooldown_counter = 0
        signals = []

        for date, is_signal in raw_signals.items():
            if is_signal and cooldown_counter == 0:
                signals.append(True)
                cooldown_counter = self.config.cooldown_days
            else:
                signals.append(False)

            if cooldown_counter > 0:
                cooldown_counter -= 1

        df["Signal"] = signals

        total_signals = sum(signals)
        logger.info(
            f"[MomentumCollapse] 偵測到 {total_signals} 個進場訊號 "
            f"(Detected {total_signals} entry signals)"
        )

        return df

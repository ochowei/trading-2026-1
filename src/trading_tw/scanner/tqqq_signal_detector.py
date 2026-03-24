"""
TQQQ 恐慌抄底訊號偵測模組 (TQQQ Capitulation Buy Signal Detector)
計算 TQQQ 專屬技術指標並偵測恐慌抄底訊號。
Computes TQQQ-specific indicators and detects capitulation buy signals.
"""

import logging

import pandas as pd

from trading_tw.scanner.tqqq_config import (
    TQQQ_COOLDOWN_DAYS,
    TQQQ_DRAWDOWN_LOOKBACK,
    TQQQ_DRAWDOWN_THRESHOLD,
    TQQQ_RSI_PERIOD,
    TQQQ_RSI_THRESHOLD,
    TQQQ_VOLUME_MULTIPLIER,
    TQQQ_VOLUME_SMA_PERIOD,
)

logger = logging.getLogger(__name__)


class TQQQSignalDetector:
    """
    TQQQ 恐慌抄底訊號偵測器 (TQQQ Capitulation Buy Signal Detector)

    三個條件同時成立時觸發訊號 (Signal triggers when all 3 conditions are met):
    1. 從 20 日高點回撤 ≥ 20% (Drawdown from 20-day high >= 20%)
    2. RSI(5) < 20 (Extreme oversold)
    3. 成交量 > 1.8x 均量 (Volume spike > 1.8x average)
    """

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """
        計算 RSI (Compute RSI using Wilder's smoothing)

        使用 Wilder 平滑法（指數移動平均），與大多數交易平台一致。
        Uses Wilder's smoothing (EMA) consistent with most trading platforms.
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        # Wilder's smoothing: EMA with alpha = 1/period
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi

    @staticmethod
    def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        計算 TQQQ 專屬技術指標 (Compute TQQQ-specific indicators)

        新增欄位 (Added columns):
        - High20: 20 日最高價的 rolling max
        - Drawdown: 從 High20 的回撤幅度
        - RSI5: 5 日 RSI
        - Volume_SMA20: 20 日成交量均線
        """
        df = df.copy()

        # 20 日最高價的滾動最大值 (Rolling max of High over 20 days)
        df["High20"] = df["High"].rolling(window=TQQQ_DRAWDOWN_LOOKBACK).max()

        # 回撤幅度 (Drawdown from 20-day high)
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]

        # RSI(5)
        df["RSI5"] = TQQQSignalDetector._compute_rsi(df["Close"], TQQQ_RSI_PERIOD)

        # 成交量均線 (Volume SMA)
        df["Volume_SMA20"] = df["Volume"].rolling(window=TQQQ_VOLUME_SMA_PERIOD).mean()

        return df

    @staticmethod
    def detect_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測恐慌抄底訊號 (Detect capitulation buy signals)

        三個條件必須同時成立 (All 3 conditions must be met):
        1. Drawdown <= -20%
        2. RSI(5) < 20
        3. Volume > 1.8x average

        包含冷卻機制：同一波跌勢中 3 個交易日內僅取第一個訊號。
        Includes cooldown: only the first signal within 3 trading days is kept.
        """
        df = df.copy()

        # 條件一: 回撤幅度 (Condition 1: Drawdown from 20-day high)
        cond_drawdown = df["Drawdown"] <= TQQQ_DRAWDOWN_THRESHOLD

        # 條件二: RSI(5) 極端超賣 (Condition 2: RSI(5) extreme oversold)
        cond_rsi = df["RSI5"] < TQQQ_RSI_THRESHOLD

        # 條件三: 成交量放大 (Condition 3: Volume spike)
        cond_volume = df["Volume"] > TQQQ_VOLUME_MULTIPLIER * df["Volume_SMA20"]

        # 合併所有條件 (Combine all conditions)
        df["Signal"] = cond_drawdown & cond_rsi & cond_volume

        # 冷卻機制：同一波跌勢中僅保留第一個訊號
        # Cooldown: suppress signals within N trading days of a prior signal
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                # 計算與上一個訊號之間的交易日數
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= TQQQ_COOLDOWN_DAYS:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info(
                f"[TQQQSignalDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號 "
                f"({len(suppressed)} duplicate signals suppressed by cooldown)"
            )

        signal_count = df["Signal"].sum()
        logger.info(
            f"[TQQQSignalDetector] TQQQ: 偵測到 {signal_count} 個恐慌抄底訊號 "
            f"({signal_count} capitulation buy signals detected)"
        )

        return df

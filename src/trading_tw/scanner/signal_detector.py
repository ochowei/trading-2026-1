"""
訊號偵測模組 (Signal Detector Module)
計算技術指標並偵測均值回歸訊號。
Computes technical indicators and detects mean-reversion signals.
"""

import logging

import numpy as np
import pandas as pd

from trading_tw.scanner.config import (
    Config,
    RSI_PERIOD,
    RSI_THRESHOLD,
    SHADOW_BODY_RATIO,
    SMA_PERIOD,
    VOLUME_MULTIPLIER,
)

logger = logging.getLogger(__name__)


class SignalDetector:
    """
    訊號偵測器 (Signal Detector)
    負責計算技術指標與偵測極端均值回歸訊號。
    Computes indicators and detects extreme mean-reversion signals.
    """

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
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
        計算所有技術指標 (Compute all technical indicators)

        新增欄位 (Added columns):
        - SMA20: 20 日簡單移動平均線
        - RSI14: 14 日 RSI
        - Bias: 乖離率 (close - SMA20) / SMA20
        - Volume_SMA20: 20 日成交量均線
        - Body: K 線實體長度
        - Lower_Shadow: 下影線長度

        Args:
            df: OHLCV DataFrame

        Returns:
            DataFrame with indicator columns added
        """
        df = df.copy()

        # 20 日簡單移動平均線 (20-day SMA)
        df["SMA20"] = df["Close"].rolling(window=SMA_PERIOD).mean()

        # 乖離率 (Bias from SMA20)
        df["Bias"] = (df["Close"] - df["SMA20"]) / df["SMA20"]

        # RSI(14) — Wilder's smoothing method
        df["RSI14"] = SignalDetector._compute_rsi(df["Close"], RSI_PERIOD)

        # 成交量 20 日均量 (20-day volume SMA)
        df["Volume_SMA20"] = df["Volume"].rolling(window=SMA_PERIOD).mean()

        # K 線實體與下影線 (Candle body and lower shadow)
        df["Body"] = (df["Close"] - df["Open"]).abs()
        df["Lower_Shadow"] = np.minimum(df["Open"], df["Close"]) - df["Low"]

        return df

    @staticmethod
    def detect_signals(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        偵測均值回歸訊號 (Detect mean-reversion signals)

        四個條件必須同時成立 (All 4 conditions must be met):
        1. 乖離率超過閾值 (Bias exceeds threshold)
        2. RSI(14) < 25
        3. 長下影線 (Long lower shadow >= 1.5x body)
        4. 成交量放大 (Volume > 1.5x average)

        Args:
            df: DataFrame with computed indicators
            ticker: 標的代碼 (Ticker symbol)

        Returns:
            DataFrame with 'Signal' boolean column added
        """
        df = df.copy()
        bias_threshold = Config.get_bias_threshold(ticker)

        # 條件一: 乖離率 (Condition 1: Bias)
        # 收盤價低於 SMA20 超過閾值
        cond_bias = df["Bias"] <= bias_threshold

        # 條件二: RSI 超賣 (Condition 2: RSI oversold)
        cond_rsi = df["RSI14"] < RSI_THRESHOLD

        # 條件三: 長下影線 (Condition 3: Long lower shadow)
        # 下影線長度 >= 1.5 倍實體長度
        # 處理十字線 (doji): 實體極小時，只要下影線 > 0 即可
        min_body = df["Close"] * 0.001  # 最小實體閾值 (minimum body threshold)
        cond_shadow = (
            (df["Lower_Shadow"] >= SHADOW_BODY_RATIO * df["Body"])
            | ((df["Body"] < min_body) & (df["Lower_Shadow"] > 0))
        )

        # 條件四: 成交量放大 (Condition 4: Volume spike)
        cond_volume = df["Volume"] > VOLUME_MULTIPLIER * df["Volume_SMA20"]

        # 合併所有條件 (Combine all conditions)
        df["Signal"] = cond_bias & cond_rsi & cond_shadow & cond_volume

        # 過濾財報日附近的訊號 (Filter signals near earnings dates)
        # 目前為預留接口 (Currently a placeholder interface)
        if df["Signal"].any():
            signal_dates = df.index[df["Signal"]]
            for date in signal_dates:
                if Config.is_near_earnings(ticker, date):
                    df.loc[date, "Signal"] = False
                    logger.info(
                        f"[SignalDetector] {ticker} {date.strftime('%Y-%m-%d')}: "
                        f"訊號因接近財報日而被過濾 (Signal filtered due to earnings proximity)"
                    )

        signal_count = df["Signal"].sum()
        logger.info(
            f"[SignalDetector] {ticker}: 偵測到 {signal_count} 個訊號 "
            f"({signal_count} signals detected)"
        )

        return df

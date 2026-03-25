"""
TQQQ 恐慌抄底訊號偵測模組 (TQQQ Capitulation Buy Signal Detector)
計算 TQQQ 專屬技術指標並偵測恐慌抄底訊號。
Computes TQQQ-specific indicators and detects capitulation buy signals.
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_capitulation.config import TQQQConfig

logger = logging.getLogger(__name__)


class TQQQSignalDetector(BaseSignalDetector):
    """
    TQQQ 恐慌抄底訊號偵測器 (TQQQ Capitulation Buy Signal Detector)

    三個條件同時成立時觸發訊號 (Signal triggers when all 3 conditions are met):
    1. 從 N 日高點回撤 ≥ threshold (Drawdown from N-day high >= threshold)
    2. RSI(period) < threshold (Extreme oversold)
    3. 成交量 > multiplier x 均量 (Volume spike > multiplier x average)
    """

    def __init__(self, config: TQQQConfig):
        self.config = config

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

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算 TQQQ 專屬技術指標 (Compute TQQQ-specific indicators)

        新增欄位 (Added columns):
        - High20: N 日最高價的 rolling max
        - Drawdown: 從 High20 的回撤幅度
        - RSI5: N 日 RSI
        - Volume_SMA20: N 日成交量均線
        """
        df = df.copy()
        cfg = self.config

        # N 日最高價的滾動最大值 (Rolling max of High)
        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()

        # 回撤幅度 (Drawdown from N-day high)
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]

        # RSI
        df["RSI5"] = self._compute_rsi(df["Close"], cfg.rsi_period)

        # 成交量均線 (Volume SMA)
        df["Volume_SMA20"] = df["Volume"].rolling(window=cfg.volume_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測恐慌抄底訊號 (Detect capitulation buy signals)

        三個條件必須同時成立 (All 3 conditions must be met):
        1. Drawdown <= threshold
        2. RSI < threshold
        3. Volume > multiplier x average

        包含冷卻機制：同一波跌勢中 N 個交易日內僅取第一個訊號。
        Includes cooldown: only the first signal within N trading days is kept.
        """
        df = df.copy()
        cfg = self.config

        # 條件一: 回撤幅度 (Condition 1: Drawdown from N-day high)
        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold

        # 條件二: RSI 極端超賣 (Condition 2: RSI extreme oversold)
        cond_rsi = df["RSI5"] < cfg.rsi_threshold

        # 條件三: 成交量放大 (Condition 3: Volume spike)
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]

        # 合併所有條件 (Combine all conditions)
        df["Signal"] = cond_drawdown & cond_rsi & cond_volume

        # 冷卻機制：同一波跌勢中僅保留第一個訊號
        # Cooldown: suppress signals within N trading days of a prior signal
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
                f"[TQQQSignalDetector] 冷卻機制抑制了 {len(suppressed)} 個重複訊號 "
                f"({len(suppressed)} duplicate signals suppressed by cooldown)"
            )

        signal_count = df["Signal"].sum()
        logger.info(
            f"[TQQQSignalDetector] TQQQ: 偵測到 {signal_count} 個恐慌抄底訊號 "
            f"({signal_count} capitulation buy signals detected)"
        )

        return df

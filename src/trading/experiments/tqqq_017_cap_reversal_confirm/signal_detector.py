"""
TQQQ-017 訊號偵測器：恐慌抄底 + 加速/確認過濾
(TQQQ-017 Signal Detector: Capitulation + Acceleration/Recovery Confirmation)

進場條件（全部同時成立，含冷卻機制）：
1. 從 20 日高點回撤 <= -15%（與 TQQQ-001/010 相同）
2. RSI(5) < 25（與 TQQQ-001/010 相同）
3. Volume > 1.5x SMA(20)（與 TQQQ-001/010 相同）
4. 【可選】ClosePos >= close_position_threshold（Att1，目前停用）
5. 【可選】2日報酬 <= two_day_return_threshold（Att2 加速過濾）
6. 【可選】Prev RSI(5) < prev_rsi_threshold（Att3 前日超賣確認）
7. 冷卻期 3 天（與 TQQQ-001/010 相同）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_017_cap_reversal_confirm.config import TQQQ017Config

logger = logging.getLogger(__name__)


class TQQQ017SignalDetector(BaseSignalDetector):
    """TQQQ-017：恐慌抄底 + 日內反轉確認訊號偵測器"""

    def __init__(self, config: TQQQ017Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder RSI（EMA 平滑）"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]
        df["RSI5"] = self._compute_rsi(df["Close"], cfg.rsi_period)
        df["Volume_SMA20"] = df["Volume"].rolling(window=cfg.volume_sma_period).mean()

        # 日內反轉位置：1.0 表收在最高、0.0 表收在最低
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # 2 日累計報酬（Att2 加速過濾用）
        df["Return2D"] = df["Close"] / df["Close"].shift(2) - 1.0

        # 前一日 RSI（Att3 前日超賣確認用）
        df["PrevRSI5"] = df["RSI5"].shift(1)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]

        df["Signal"] = cond_drawdown & cond_rsi & cond_volume

        # 可選：ClosePos 日內反轉過濾
        if cfg.close_position_threshold > 0:
            df["Signal"] &= df["ClosePos"] >= cfg.close_position_threshold

        # 可選：2 日加速跌幅過濾（Att2）
        if cfg.enable_two_day_filter:
            df["Signal"] &= df["Return2D"] <= cfg.two_day_return_threshold

        # 可選：前日 RSI 超賣確認（Att3）
        if cfg.prev_rsi_threshold > 0:
            df["Signal"] &= df["PrevRSI5"] < cfg.prev_rsi_threshold

        # 冷卻機制（同 TQQQ-001）
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap_days = len(df.loc[last_signal:idx]) - 1
                if gap_days <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("TQQQ-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TQQQ-017: Detected %d capitulation + reversal-confirmed signals", signal_count)
        return df

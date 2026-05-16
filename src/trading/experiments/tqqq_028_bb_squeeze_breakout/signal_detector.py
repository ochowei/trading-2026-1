"""TQQQ-028 TQQQ BB Squeeze Breakout 訊號偵測器

進場條件（T 日為訊號日，T+1 開盤進場）：
  1. 前日 BB(20,2) 寬度/Close < squeeze_max_bb_width（波動率收縮 squeeze）
  2. 當日 Close > BB_Upper（上軌突破 = 趨勢啟動 ignition）
  3. （可選 Att3）當日 Volume > volume_multiplier x SMA20
  4. 冷卻期 cooldown_days 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_028_bb_squeeze_breakout.config import TQQQ028Config

logger = logging.getLogger(__name__)


class TQQQ028SignalDetector(BaseSignalDetector):
    """TQQQ-028：TQQQ 自身 BB squeeze + 上軌突破"""

    def __init__(self, config: TQQQ028Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        sma = df["Close"].rolling(cfg.bb_period).mean()
        std = df["Close"].rolling(cfg.bb_period).std()
        df["BB_Upper"] = sma + cfg.bb_std * std
        df["BB_Lower"] = sma - cfg.bb_std * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        df["Volume_SMA20"] = df["Volume"].rolling(cfg.volume_sma_period).mean()

        df["Trend_SMA"] = df["Close"].rolling(cfg.trend_sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # 前日處於 squeeze（波動率收縮）
        cond_squeeze = df["BB_Width_Ratio"].shift(1) < cfg.squeeze_max_bb_width

        if cfg.require_breakout:
            cond_breakout = df["Close"] > df["BB_Upper"]
        else:
            cond_breakout = pd.Series(True, index=df.index)

        if cfg.use_volume_filter:
            cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        else:
            cond_volume = pd.Series(True, index=df.index)

        if cfg.use_trend_filter:
            cond_trend = df["Close"] > df["Trend_SMA"]
        else:
            cond_trend = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_squeeze.fillna(False) & cond_breakout & cond_volume & cond_trend.fillna(False)
        )

        # 冷卻機制
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
                "TQQQ-028: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-028: Detected %d BB-squeeze-breakout signals "
            "(squeeze < %.2f, breakout=%s, vol filter=%s)",
            signal_count,
            cfg.squeeze_max_bb_width,
            cfg.require_breakout,
            cfg.use_volume_filter,
        )
        return df

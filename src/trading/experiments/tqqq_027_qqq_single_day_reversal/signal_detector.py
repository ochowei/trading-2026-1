"""TQQQ-027 QQQ Single-Day Momentum-Reversal 訊號偵測器

進場條件（T 日為訊號日，T+1 開盤買 TQQQ）：
  1. QQQ 單日報酬 ROC(1) <= qqq_roc1_threshold（單日急跌）
  2. QQQ 當日 ClosePos = (Close-Low)/(High-Low) >= qqq_min_closepos
     （收於日內區間上半部 = 日內反轉，多方尾盤承接）
  3. （可選 Att3）QQQ 量能 > qqq_volume_multiplier x SMA20
  4. 冷卻期 cooldown_days 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tqqq_027_qqq_single_day_reversal.config import TQQQ027Config

logger = logging.getLogger(__name__)


class TQQQ027SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """QQQ 單日動量反轉訊號偵測器（訊號基於 QQQ，交易 TQQQ）"""

    def __init__(self, config: TQQQ027Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.qqq_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config
        qqq = self.require_auxiliary(cfg.qqq_ticker, df.index)

        q_close = qqq["Close"]
        q_high = qqq["High"]
        q_low = qqq["Low"]

        df["QQQ_ROC1"] = q_close.pct_change(1) * 100
        rng = (q_high - q_low).replace(0.0, float("nan"))
        df["QQQ_ClosePos"] = (q_close - q_low) / rng

        q_vol = qqq["Volume"]
        q_vol_sma = q_vol.rolling(cfg.qqq_volume_sma_period).mean()
        df["QQQ_Vol_Spike"] = q_vol > cfg.qqq_volume_multiplier * q_vol_sma

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        if "QQQ_ROC1" not in df.columns:
            df["Signal"] = False
            return df

        cond_drop = df["QQQ_ROC1"].fillna(0.0) <= cfg.qqq_roc1_threshold
        cond_reversal = df["QQQ_ClosePos"].fillna(0.0) >= cfg.qqq_min_closepos

        if cfg.use_qqq_volume_filter:
            cond_vol = df["QQQ_Vol_Spike"].fillna(False)
        else:
            cond_vol = pd.Series(True, index=df.index)

        df["Signal"] = cond_drop & cond_reversal & cond_vol

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
                "TQQQ-027: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-027: Detected %d QQQ single-day-reversal signals "
            "(ROC1 <= %.2f%%, ClosePos >= %.2f, vol filter=%s)",
            signal_count,
            cfg.qqq_roc1_threshold,
            cfg.qqq_min_closepos,
            cfg.use_qqq_volume_filter,
        )
        return df

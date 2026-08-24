"""TQQQ-030 TQQQ Dual-Horizon Momentum Continuation 訊號偵測器

進場條件（T 日為訊號日，T+1 開盤進場）：
  1. ROC(roc_short) > roc_short_threshold（短時框動量）
  2. ROC(roc_medium) > roc_medium_threshold（中時框動量持續堆疊）
  3. Close > SMA(trend_sma_period)（趨勢確認）
  4. （可選 Att2）Close > SMA(bull_sma_period)（長期 bull regime）
  5. （可選 Att3）BB 寬度/Close < max_bb_width_ratio（避開極端 vol regime）
  6. 冷卻期 cooldown_days 天
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_030_dual_momentum.config import TQQQ030Config

logger = logging.getLogger(__name__)


class TQQQ030SignalDetector(BaseSignalDetector):
    """TQQQ-030：TQQQ 自身雙時框動量堆疊持續性（動量）"""

    def __init__(self, config: TQQQ030Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        df["ROC_Short"] = df["Close"].pct_change(cfg.roc_short_period) * 100
        df["ROC_Medium"] = df["Close"].pct_change(cfg.roc_medium_period) * 100
        df["Trend_SMA"] = df["Close"].rolling(cfg.trend_sma_period).mean()
        df["Bull_SMA"] = df["Close"].rolling(cfg.bull_sma_period).mean()

        std = df["Close"].rolling(cfg.bb_period).std()
        df["BB_Width_Ratio"] = (2 * cfg.bb_std * std) / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_roc_s = df["ROC_Short"].fillna(-999.0) > cfg.roc_short_threshold
        cond_roc_m = df["ROC_Medium"].fillna(-999.0) > cfg.roc_medium_threshold
        cond_trend = df["Close"] > df["Trend_SMA"]

        if cfg.use_bull_filter:
            cond_bull = df["Close"] > df["Bull_SMA"]
        else:
            cond_bull = pd.Series(True, index=df.index)

        if cfg.use_vol_cap:
            cond_vol = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        else:
            cond_vol = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_roc_s
            & cond_roc_m
            & cond_trend.fillna(False)
            & cond_bull.fillna(False)
            & cond_vol.fillna(False)
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
                "TQQQ-030: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-030: Detected %d dual-momentum signals "
            "(ROC%d>%.1f%% & ROC%d>%.1f%%, bull=%s, vol_cap=%s)",
            signal_count,
            cfg.roc_short_period,
            cfg.roc_short_threshold,
            cfg.roc_medium_period,
            cfg.roc_medium_threshold,
            cfg.use_bull_filter,
            cfg.use_vol_cap,
        )
        return df

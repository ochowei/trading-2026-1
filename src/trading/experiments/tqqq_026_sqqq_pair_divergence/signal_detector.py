"""TQQQ-026 TQQQ/SQQQ Inverse-Pair Capitulation Confirmation 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1-5. 同 TQQQ-018 Att3（DD≤-15% + RSI(5)<25 + Vol>1.5x + BB-width<0.48
       + DD(T-5)≤-1%）
  6.  **SQQQ RSI(5) >= min_sqqq_rsi**（TQQQ-026 核心新增：inverse-pair
      恐慌極端確認；過濾 TQQQ 緩跌而 SQQQ 並未進入恐慌極端的低品質訊號）
  6b. （可選 Att3）SQQQ 量能 > 1.5x SMA20（inverse-pair 量能耗竭確認）
  7.  冷卻期 3 天（同 TQQQ-018）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_026_sqqq_pair_divergence.config import TQQQ026Config

logger = logging.getLogger(__name__)


class TQQQ026SignalDetector(BaseSignalDetector):
    """TQQQ-026：TQQQ-018 框架 + SQQQ inverse-pair 恐慌確認 filter"""

    def __init__(self, config: TQQQ026Config):
        self.config = config
        self._base_detector = TQQQ018SignalDetector(config)

    def _fetch_ohlcv(self, ticker: str, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                ticker,
                start=start_date,
                progress=False,
                auto_adjust=True,
            )
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception:
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._base_detector.compute_indicators(df)

        cfg = self.config
        start_date = df.index[0].strftime("%Y-%m-%d")

        sqqq = self._fetch_ohlcv(cfg.sqqq_ticker, start_date)
        if sqqq is None:
            logger.error("無法取得 %s 數據，SQQQ 配對過濾停用", cfg.sqqq_ticker)
            df["SQQQ_RSI"] = float("nan")
            df["SQQQ_Vol_Spike"] = False
            return df

        sqqq_close = sqqq["Close"].reindex(df.index, method="ffill")
        df["SQQQ_RSI"] = TQQQSignalDetector._compute_rsi(sqqq_close, cfg.sqqq_rsi_period)

        sqqq_vol = sqqq["Volume"].reindex(df.index, method="ffill")
        sqqq_vol_sma = sqqq_vol.rolling(cfg.sqqq_volume_sma_period).mean()
        df["SQQQ_Vol_Spike"] = sqqq_vol > cfg.sqqq_volume_multiplier * sqqq_vol_sma

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        if cfg.use_sqqq_rsi_filter:
            # 缺值（暖機/假日）保守填 0（不滿足 FLOOR → 不發訊號）
            sqqq_rsi = df["SQQQ_RSI"].fillna(0.0)
            cond_sqqq_rsi = sqqq_rsi >= cfg.min_sqqq_rsi
        else:
            cond_sqqq_rsi = pd.Series(True, index=df.index)

        if cfg.use_sqqq_volume_filter:
            cond_sqqq_vol = df["SQQQ_Vol_Spike"].fillna(False)
        else:
            cond_sqqq_vol = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_drawdown
            & cond_rsi
            & cond_volume
            & cond_regime
            & cond_prior_dd
            & cond_sqqq_rsi
            & cond_sqqq_vol
        )

        # 冷卻機制（同 TQQQ-018）
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
                "TQQQ-026: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-026: Detected %d SQQQ-pair-confirmed capitulation signals "
            "(SQQQ RSI >= %.1f, vol filter=%s)",
            signal_count,
            cfg.min_sqqq_rsi,
            cfg.use_sqqq_volume_filter,
        )
        return df

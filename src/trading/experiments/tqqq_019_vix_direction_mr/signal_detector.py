"""TQQQ-019 ^VIX Direction Filter on Vol-Regime-Gated Capitulation Buy 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-001 / TQQQ-010 / TQQQ-018）
  2. RSI(5) < 25（同上）
  3. 成交量 > 1.5 × 20 日成交量均線（同上）
  4. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（同 TQQQ-018 vol regime gate）
  5. Drawdown(T-N) <= prior_drawdown_threshold（同 TQQQ-018 prior DD filter）
  6. ^VIX N 日累計變化 <= max_vix_direction_change（TQQQ-019 核心新增）
  7. 冷卻期 3 天（同上）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_019_vix_direction_mr.config import TQQQ019Config

logger = logging.getLogger(__name__)


class TQQQ019SignalDetector(BaseSignalDetector):
    """TQQQ-019：TQQQ-018 框架 + ^VIX direction filter"""

    def __init__(self, config: TQQQ019Config):
        self.config = config
        self._base_detector = TQQQ018SignalDetector(config)

    def _fetch_vix_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.vix_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.vix_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._base_detector.compute_indicators(df)

        cfg = self.config
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_vix_data(start_date)

        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，^VIX direction 過濾停用", cfg.vix_ticker)
            df["VIX_Close"] = float("nan")
            df["VIX_Direction_Change"] = 0.0
        else:
            vix_close = vix_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Close"] = vix_close
            df["VIX_Direction_Change"] = vix_close.diff(cfg.vix_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        if cfg.use_vix_direction_filter:
            vix_change = df["VIX_Direction_Change"].fillna(-999.0)
            cond_vix_dir = vix_change <= cfg.max_vix_direction_change
        else:
            cond_vix_dir = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_drawdown & cond_rsi & cond_volume & cond_regime & cond_prior_dd & cond_vix_dir
        )

        # 冷卻機制（同 TQQQ-001 / TQQQ-018）
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
                "TQQQ-019: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-019: Detected %d VIX-direction-gated capitulation signals "
            "(^VIX %dd change <= %+.1f)",
            signal_count,
            cfg.vix_direction_lookback,
            cfg.max_vix_direction_change,
        )
        return df

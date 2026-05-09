"""TQQQ-023 訊號偵測器：Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-018）
  2. RSI(5) < 25（同 TQQQ-018）
  3. 成交量 > 1.5 × 20 日成交量均線（同 TQQQ-018）
  4. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（同 TQQQ-018）
  5. DD(T-5) <= prior_drawdown_threshold（同 TQQQ-018）
  6. **(^TYX - ^TNX) N 日 slope velocity <= max_slope_change**
     （TQQQ-023 新增：yield curve slope velocity inflation-regime gate）
  7. 冷卻期 3 天（同 TQQQ-018）

跨資產移植自 TLT-017 lesson #24 family v10 (yield curve slope velocity)，
首次自 rate-direct asset (TLT) 跨資產類別移植至 leveraged tech ETF (TQQQ)。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_023_yield_curve_slope_cap.config import TQQQ023Config

logger = logging.getLogger(__name__)


class TQQQ023YieldCurveSlopeDetector(BaseSignalDetector):
    """TQQQ-023：恐慌抄底 + 波動率 regime + first-day filter + yield curve slope velocity"""

    def __init__(self, config: TQQQ023Config):
        self.config = config
        self._base_detector = TQQQ018SignalDetector(config)

    @staticmethod
    def _fetch_external(ticker: str, start_date: str) -> pd.DataFrame | None:
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
        long_yield_df = self._fetch_external(cfg.long_yield_ticker, start_date)
        short_yield_df = self._fetch_external(cfg.short_yield_ticker, start_date)

        if (
            long_yield_df is None
            or long_yield_df.empty
            or short_yield_df is None
            or short_yield_df.empty
        ):
            logger.error(
                "無法取得 %s / %s 數據, yield curve slope 過濾停用",
                cfg.long_yield_ticker,
                cfg.short_yield_ticker,
            )
            df["Yield_Slope"] = float("nan")
            df["Slope_Change_N"] = 0.0
        else:
            long_yield = long_yield_df["Close"].reindex(df.index, method="ffill")
            short_yield = short_yield_df["Close"].reindex(df.index, method="ffill")
            slope = long_yield - short_yield
            df["Yield_Slope"] = slope
            df["Slope_Change_N"] = slope.diff(cfg.slope_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        signal = cond_drawdown & cond_rsi & cond_volume & cond_regime & cond_prior_dd

        if cfg.use_slope_change_filter:
            # NaN 視為通過（fallback 為包容，避免無 yield 數據日全部過濾）
            slope_change = df["Slope_Change_N"].fillna(-999.0)
            cond_slope_change = slope_change <= cfg.max_slope_change
            signal = signal & cond_slope_change

        if cfg.use_slope_level_filter:
            slope_level = df["Yield_Slope"].fillna(-999.0)
            cond_slope_level = slope_level <= cfg.max_slope_level
            signal = signal & cond_slope_level

        df["Signal"] = signal.fillna(False)

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
                "TQQQ-023: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-023: Detected %d yield-curve-slope-gated capitulation signals",
            signal_count,
        )
        return df

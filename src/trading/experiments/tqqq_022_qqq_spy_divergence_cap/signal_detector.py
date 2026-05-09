"""TQQQ-022 訊號偵測器：QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-018）
  2. RSI(5) < 25（同 TQQQ-018）
  3. 成交量 > 1.5 × 20 日成交量均線（同 TQQQ-018）
  4. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（同 TQQQ-018）
  5. DD(T-5) <= prior_drawdown_threshold（同 TQQQ-018）
  6. **QQQ 20 日報酬 - SPY 20 日報酬 >= min_relative_return**
     （TQQQ-022 新增：cross-asset divergence FLOOR regime gate）
  7. 冷卻期 3 天（同 TQQQ-018）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_022_qqq_spy_divergence_cap.config import TQQQ022Config

logger = logging.getLogger(__name__)


class TQQQ022QQQSPYDivergenceDetector(BaseSignalDetector):
    """TQQQ-022：恐慌抄底 + 波動率 regime + first-day filter + QQQ-SPY 跨資產 FLOOR"""

    def __init__(self, config: TQQQ022Config):
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
        qqq_df = self._fetch_external(cfg.qqq_ticker, start_date)
        spy_df = self._fetch_external(cfg.spy_ticker, start_date)

        n = cfg.divergence_lookback
        if qqq_df is None or qqq_df.empty or spy_df is None or spy_df.empty:
            logger.error(
                "無法取得 QQQ/SPY 數據，cross-asset divergence 過濾停用 "
                "(Failed to fetch QQQ/SPY, divergence filter disabled)"
            )
            df["QQQ_Ret_N"] = 0.0
            df["SPY_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            qqq_close = qqq_df["Close"].reindex(df.index, method="ffill")
            spy_close = spy_df["Close"].reindex(df.index, method="ffill")
            df["QQQ_Ret_N"] = qqq_close.pct_change(n)
            df["SPY_Ret_N"] = spy_close.pct_change(n)
            df["Rel_Return_N"] = df["QQQ_Ret_N"] - df["SPY_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        if cfg.use_divergence_filter:
            cond_divergence = df["Rel_Return_N"].fillna(0.0) >= cfg.min_relative_return
        else:
            cond_divergence = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_drawdown & cond_rsi & cond_volume & cond_regime & cond_prior_dd & cond_divergence
        )

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
                "TQQQ-022: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-022: Detected %d divergence-gated capitulation signals",
            signal_count,
        )
        return df

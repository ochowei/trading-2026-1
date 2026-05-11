"""TQQQ-025 VXN-VIX Cross-Index Divergence + VVIX Direction Filter 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-001 / TQQQ-010 / TQQQ-018）
  2. RSI(5) < 25（同上）
  3. 成交量 > 1.5 × 20 日成交量均線（同上）
  4. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（同 TQQQ-018 vol regime gate）
  5. Drawdown(T-N) <= prior_drawdown_threshold（同 TQQQ-018 prior DD filter）
  6. **^VXN / ^VIX 比率 >= min_vxn_vix_ratio**（TQQQ-025 核心新增維度 1：
     cross-index implied vol divergence；過濾 tech 並未顯著跑輸大盤的廣泛恐慌訊號）
  6b. （可選）^VVIX N 日累計變化 >= min_vvix_direction_change（Att2/Att3 啟用：
       higher-moment IV direction；過濾 VVIX 急速下行的 uncertainty resolving 訊號）
  7. 冷卻期 3 天（同上）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_025_vxn_vix_vvix_filter.config import TQQQ025Config

logger = logging.getLogger(__name__)


class TQQQ025SignalDetector(BaseSignalDetector):
    """TQQQ-025：TQQQ-018 框架 + ^VXN/^VIX 比率 + ^VVIX 方向 filter"""

    def __init__(self, config: TQQQ025Config):
        self.config = config
        self._base_detector = TQQQ018SignalDetector(config)

    def _fetch_close_series(self, ticker: str, start_date: str) -> pd.Series | None:
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
            return df["Close"]
        except Exception:
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._base_detector.compute_indicators(df)

        cfg = self.config
        start_date = df.index[0].strftime("%Y-%m-%d")

        vxn_close = self._fetch_close_series(cfg.vxn_ticker, start_date)
        vix_close = self._fetch_close_series(cfg.vix_ticker, start_date)
        vvix_close = self._fetch_close_series(cfg.vvix_ticker, start_date)

        if vxn_close is None or vix_close is None:
            logger.error(
                "無法取得 %s 或 %s 數據，VXN/VIX 過濾停用",
                cfg.vxn_ticker,
                cfg.vix_ticker,
            )
            df["VXN_VIX_Ratio"] = float("nan")
        else:
            vxn_aligned = vxn_close.reindex(df.index, method="ffill")
            vix_aligned = vix_close.reindex(df.index, method="ffill")
            df["VXN_VIX_Ratio"] = vxn_aligned / vix_aligned

        if vvix_close is None:
            logger.error("無法取得 %s 數據，VVIX 方向過濾停用", cfg.vvix_ticker)
            df["VVIX_Close"] = float("nan")
            df["VVIX_Direction_Change"] = 0.0
        else:
            vvix_aligned = vvix_close.reindex(df.index, method="ffill")
            df["VVIX_Close"] = vvix_aligned
            df["VVIX_Direction_Change"] = vvix_aligned.diff(cfg.vvix_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        if cfg.use_vxn_vix_filter:
            # 缺值（^VXN/^VIX 暖機期或假日）保守填 0（不滿足 FLOOR → 不發訊號）
            ratio = df["VXN_VIX_Ratio"].fillna(0.0)
            cond_vxn_vix = ratio >= cfg.min_vxn_vix_ratio
        else:
            cond_vxn_vix = pd.Series(True, index=df.index)

        if cfg.use_vvix_direction_filter:
            # 缺值保守填 -999（不滿足 FLOOR → 不發訊號）
            vvix_dir = df["VVIX_Direction_Change"].fillna(-999.0)
            cond_vvix_dir = vvix_dir >= cfg.min_vvix_direction_change
        else:
            cond_vvix_dir = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_drawdown
            & cond_rsi
            & cond_volume
            & cond_regime
            & cond_prior_dd
            & cond_vxn_vix
            & cond_vvix_dir
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
                "TQQQ-025: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-025: Detected %d VXN/VIX-gated capitulation signals "
            "(VXN/VIX >= %.3f, VVIX dir filter=%s)",
            signal_count,
            cfg.min_vxn_vix_ratio,
            cfg.use_vvix_direction_filter,
        )
        return df

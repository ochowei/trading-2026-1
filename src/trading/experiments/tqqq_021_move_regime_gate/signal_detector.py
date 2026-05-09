"""TQQQ-021 ^MOVE Bond-Vol LEVEL Regime Gate on Vol-Regime-Gated Capitulation Buy 訊號偵測器

進場條件（全部滿足，T 日為訊號日，T+1 開盤進場）：
  1. 從 20 日高點回撤 ≤ -15%（同 TQQQ-001 / TQQQ-010 / TQQQ-018）
  2. RSI(5) < 25（同上）
  3. 成交量 > 1.5 × 20 日成交量均線（同上）
  4. BB(20, 2) 通道寬度 / Close < max_bb_width_ratio（同 TQQQ-018 vol regime gate）
  5. Drawdown(T-N) <= prior_drawdown_threshold（同 TQQQ-018 prior DD filter）
  6. **^MOVE 今日收盤 <= max_move_level**（TQQQ-021 核心新增：bond vol LEVEL
     filter；與 ^VIX DIRECTION 維度（TQQQ-019/020）正交，repo 首次 ^MOVE 於
     leveraged 槓桿股票 ETF）
  6b. （可選）^MOVE N 日累計變化 <= max_move_direction_change（Att2/Att3 啟用）
  7. 冷卻期 3 天（同上）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tqqq_018_regime_vol_gate.signal_detector import (
    TQQQ018SignalDetector,
)
from trading.experiments.tqqq_021_move_regime_gate.config import TQQQ021Config

logger = logging.getLogger(__name__)


class TQQQ021SignalDetector(BaseSignalDetector):
    """TQQQ-021：TQQQ-018 框架 + ^MOVE LEVEL filter"""

    def __init__(self, config: TQQQ021Config):
        self.config = config
        self._base_detector = TQQQ018SignalDetector(config)

    def _fetch_move_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.move_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.move_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._base_detector.compute_indicators(df)

        cfg = self.config
        start_date = df.index[0].strftime("%Y-%m-%d")
        move_df = self._fetch_move_data(start_date)

        if move_df is None or move_df.empty:
            logger.error("無法取得 %s 數據，^MOVE LEVEL 過濾停用", cfg.move_ticker)
            df["MOVE_Close"] = float("nan")
            df["MOVE_Direction_Change"] = 0.0
        else:
            move_close = move_df["Close"].reindex(df.index, method="ffill")
            df["MOVE_Close"] = move_close
            df["MOVE_Direction_Change"] = move_close.diff(cfg.move_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_volume = df["Volume"] > cfg.volume_multiplier * df["Volume_SMA20"]
        cond_regime = df["BB_Width_Ratio"] < cfg.max_bb_width_ratio
        cond_prior_dd = df["Drawdown_Prior"].fillna(0.0) <= cfg.prior_drawdown_threshold

        if cfg.use_move_level_filter:
            # 缺值（^MOVE 未發行期或暖機期）保守填 +999（不滿足 LEVEL cap → 不發訊號）
            move_level = df["MOVE_Close"].fillna(999.0)
            cond_move_level = move_level <= cfg.max_move_level
        else:
            cond_move_level = pd.Series(True, index=df.index)

        if cfg.use_move_direction_filter:
            move_dir = df["MOVE_Direction_Change"].fillna(999.0)
            cond_move_dir = move_dir <= cfg.max_move_direction_change
        else:
            cond_move_dir = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_drawdown
            & cond_rsi
            & cond_volume
            & cond_regime
            & cond_prior_dd
            & cond_move_level
            & cond_move_dir
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
                "TQQQ-021: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "TQQQ-021: Detected %d MOVE-level-gated capitulation signals "
            "(^MOVE level <= %.1f, dir filter=%s)",
            signal_count,
            cfg.max_move_level,
            cfg.use_move_direction_filter,
        )
        return df

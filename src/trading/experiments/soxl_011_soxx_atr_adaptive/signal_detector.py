"""
SOXL-011 訊號偵測器：SOXX ATR-Adaptive Mean Reversion

進場條件（全部滿足）：
1. SOXL 從 20 日高點回撤在 [-40%, -25%]（同 SOXL-006）
2. SOXL RSI(5) < 20（同 SOXL-006）
3. SOXL 2 日累積跌幅 <= -8%（同 SOXL-006）
4. SOXX ATR(5)/ATR(20) > 1.1（底層指數波動率擴張過濾）
5. 冷卻期 7 個交易日

結果：Part A Sharpe 0.34 / Part B Sharpe 0.79，min(A,B) 0.34
ATR 過濾移除 3 個 Part A 訊號（2 好/1 壞），未改善基線
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.soxl_011_soxx_atr_adaptive.config import SOXLSoxxAtrConfig

logger = logging.getLogger(__name__)


class SOXLSoxxAtrDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """SOXL SOXX ATR-Adaptive 均值回歸訊號偵測器"""

    def __init__(self, config: SOXLSoxxAtrConfig):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """計算 RSI (Wilder's smoothing)"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """計算 ATR (Average True Range)"""
        high = df["High"]
        low = df["Low"]
        close = df["Close"].shift(1)
        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period, min_periods=period).mean()

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.soxx_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標（SOXL + SOXX ATR）"""
        df = df.copy()
        cfg = self.config

        # SOXL indicators (same as SOXL-006)
        df["High20"] = df["High"].rolling(window=cfg.drawdown_lookback).max()
        df["Drawdown"] = (df["Close"] - df["High20"]) / df["High20"]
        df["RSI5"] = self._compute_rsi(df["Close"], cfg.rsi_period)
        df["Drop2D"] = df["Close"].pct_change(periods=2)

        # SOXX ATR ratio
        soxx_df = self.require_auxiliary(self.config.soxx_ticker, df.index)
        atr_fast = self._compute_atr(soxx_df, cfg.atr_fast_period)
        atr_slow = self._compute_atr(soxx_df, cfg.atr_slow_period)
        df["SOXX_ATR_Ratio"] = atr_fast / atr_slow

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """偵測 SOXX ATR-Adaptive 均值回歸訊號"""
        df = df.copy()
        cfg = self.config

        # SOXL conditions (same as SOXL-006)
        cond_drawdown = df["Drawdown"] <= cfg.drawdown_threshold
        cond_cap = df["Drawdown"] >= cfg.drawdown_cap
        cond_rsi = df["RSI5"] < cfg.rsi_threshold
        cond_drop2d = df["Drop2D"] <= cfg.drop_2d_threshold

        # SOXX ATR volatility expansion filter
        cond_atr = df["SOXX_ATR_Ratio"] > cfg.atr_ratio_threshold

        df["Signal"] = cond_drawdown & cond_cap & cond_rsi & cond_drop2d & cond_atr

        # Cooldown mechanism
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
                "SOXX ATR-Adaptive: cooldown suppressed %d duplicate signals",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info("SOXL: Detected %d SOXX ATR-adaptive signals", signal_count)
        return df

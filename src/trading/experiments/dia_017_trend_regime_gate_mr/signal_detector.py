"""
DIA-017 訊號偵測器：Buffered Multi-Week SMA Trend-Regime-Gated MR

在 DIA-012 Att2 五條件 MR 進場邏輯之上，新增 lesson #22 buffered
multi-week SMA 趨勢 regime 閘門：

  SMA(sma_fast) >= regime_k × SMA(sma_slow)
  [可選] AND Close > SMA(sma_long)

pre-analysis 預期 reverse-selection 結構性失敗：DIA-012 殘餘 SL 2022-01-18
處於偽多頭 regime（通過 bull gate），而 DIA 最佳 MR 贏家為 bear-regime
oversold 進場（被 bull gate 移除）——建立 lesson #22 family 失敗邊界。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_017_trend_regime_gate_mr.config import DIA017Config

logger = logging.getLogger(__name__)


class DIA017SignalDetector(BaseSignalDetector):
    """Buffered Multi-Week SMA Trend-Regime-Gated MR 訊號偵測器"""

    def __init__(self, config: DIA017Config):
        self.config = config

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)（沿用 DIA-012）
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2 日累計跌幅（沿用 DIA-012）
        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 1 日 / 3 日報酬（沿用 DIA-012）
        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_3d"] = df["Close"].pct_change(3)

        # 收盤位置（沿用 DIA-012）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === DIA-017 核心新增：lesson #22 buffered multi-week SMA regime ===
        df["SMA_fast"] = df["Close"].rolling(self.config.sma_fast).mean()
        df["SMA_slow"] = df["Close"].rolling(self.config.sma_slow).mean()
        df["SMA_long"] = df["Close"].rolling(self.config.sma_long).mean()
        df["SMA_ratio"] = df["SMA_fast"] / df["SMA_slow"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap

        # lesson #22 buffered SMA trend regime gate
        cond_regime = df["SMA_fast"] >= self.config.regime_k * df["SMA_slow"]
        if self.config.require_above_long:
            cond_regime = cond_regime & (df["Close"] > df["SMA_long"])

        df["Signal"] = (
            cond_rsi
            & cond_decline
            & cond_reversal
            & cond_oneday_cap
            & cond_threeday_cap
            & cond_regime
        )

        # Cooldown（沿用 DIA-012）
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("DIA-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-017: Detected %d signals (k=%.3f, require_above_long=%s)",
            signal_count,
            self.config.regime_k,
            self.config.require_above_long,
        )
        return df

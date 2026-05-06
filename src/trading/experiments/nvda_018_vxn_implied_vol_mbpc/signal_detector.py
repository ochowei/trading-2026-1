"""
NVDA-018 訊號偵測器：^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated MBPC

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 近 breakout_recency_days 日內 High 曾突破前 donchian_period 日最高價
2. Close > SMA(sma_trend_period)
3. SMA(sma_regime_short) ≥ sma_regime_ratio_min × SMA(sma_regime_long)
   （lesson #22 buffered multi-week SMA regime gate）
4. 5 日高點回檔 ∈ [pullback_max, pullback_min]
5. RSI(rsi_period) ∈ [rsi_min, rsi_max]
6. Close > Open（多頭 K 棒確認）
7. ATR(atr_regime_short) ≤ vol_regime_max_ratio × ATR(atr_regime_long)
   （lesson #22 ATR vol regime，MBPC 框架非冗餘）
8. ^VXN N 日變化 ≤ max_vxn_change（NVDA-018 核心新增 forward-looking IV gate）
9. 冷卻 cooldown_days 個交易日

跨資產移植自 USO-025 / XLU-013 / GLD-015 / TLT-013 lesson #24 family，
首次驗證於 mega-cap 個股 + MBPC 框架。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.nvda_018_vxn_implied_vol_mbpc.config import NVDA018Config

logger = logging.getLogger(__name__)


class NVDA018SignalDetector(BaseSignalDetector):
    """NVDA-018：NVDA-013 Att3 + ^VXN forward-looking implied vol DIRECTION gate"""

    def __init__(self, config: NVDA018Config):
        self.config = config

    @staticmethod
    def _compute_rsi(close: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.where(avg_loss > 0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def _fetch_vxn_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.vxn_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.vxn_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Donchian breakout freshness ===
        donchian = df["High"].shift(1).rolling(self.config.donchian_period).max()
        df["Donchian_Upper"] = donchian
        df["IsNewHigh"] = df["High"] > donchian
        recency = self.config.breakout_recency_days
        df["RecentNewHigh"] = df["IsNewHigh"].rolling(recency, min_periods=1).max().fillna(0) >= 1.0

        # === SMA trend filter ===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === Multi-week SMA regime (lesson #22) ===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === Pullback from recent high ===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === RSI(14) ===
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # === ATR regime ===
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["ATR_Regime_Short"] = df["TR"].rolling(self.config.atr_regime_short).mean()
        df["ATR_Regime_Long"] = df["TR"].rolling(self.config.atr_regime_long).mean()

        # === ^VXN forward-looking implied vol gate（NVDA-018 核心新增）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vxn_df = self._fetch_vxn_data(start_date)

        if vxn_df is None or vxn_df.empty:
            logger.error("無法取得 %s 數據，^VXN 過濾停用", self.config.vxn_ticker)
            df["VXN_Close"] = float("nan")
            df["VXN_Change_Nd"] = 0.0
        else:
            vxn_close = vxn_df["Close"].reindex(df.index, method="ffill")
            df["VXN_Close"] = vxn_close
            df["VXN_Change_Nd"] = vxn_close.diff(self.config.vxn_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_recent_new_high = df["RecentNewHigh"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )
        cond_pullback_min = df["Pullback"] <= self.config.pullback_min
        cond_pullback_max = df["Pullback"] >= self.config.pullback_max
        cond_rsi_min = df["RSI"] >= self.config.rsi_min
        cond_rsi_max = df["RSI"] <= self.config.rsi_max
        if self.config.use_vol_regime:
            cond_regime_vol = df["ATR_Regime_Short"] <= (
                df["ATR_Regime_Long"] * self.config.vol_regime_max_ratio
            )
        else:
            cond_regime_vol = pd.Series(True, index=df.index)

        if self.config.use_vxn_direction_filter:
            # NaN 視為通過（fallback 為包容，避免無 VXN 數據日全部過濾）
            vxn_change = df["VXN_Change_Nd"].fillna(-999.0)
            cond_vxn_dir = vxn_change <= self.config.max_vxn_change
        else:
            cond_vxn_dir = pd.Series(True, index=df.index)

        if self.config.use_vxn_level_cap:
            vxn_level = df["VXN_Close"].fillna(0.0)
            cond_vxn_level = vxn_level <= self.config.max_vxn_level
        else:
            cond_vxn_level = pd.Series(True, index=df.index)

        signal = (
            cond_recent_new_high
            & cond_trend
            & cond_regime_trend
            & cond_pullback_min
            & cond_pullback_max
            & cond_rsi_min
            & cond_rsi_max
            & cond_regime_vol
            & cond_vxn_dir
            & cond_vxn_level
        )

        if self.config.bullish_close_required:
            signal = signal & (df["Close"] > df["Open"])

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
            logger.info(
                "NVDA-018: %d signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "NVDA-018: Detected %d ^VXN-IV-direction-gated MBPC signals",
            signal_count,
        )
        return df

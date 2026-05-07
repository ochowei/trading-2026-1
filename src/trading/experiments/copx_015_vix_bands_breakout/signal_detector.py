"""
COPX-015 訊號偵測器：^VIX Implied-Vol Regime Filter on Multi-Week Regime-Aware
                    BB Squeeze Breakout

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 COPX-011）
2. 收盤價 > Upper BB(20, 2.0)（同 COPX-011）
3. 收盤價 > SMA(50)（同 COPX-011）
4. regime BOX：1.00 <= SMA(20) / SMA(60) <= 1.09（lesson #22 + COPX-011 BOX）
5. **^VIX 收盤值滿足 vix_filter_mode 條件**
   （COPX-015 新增 lesson #24 FLOOR 變體 cross-asset port from FCX-015 Att2）
6. 冷卻 cooldown_days 個交易日

設計依據：lesson #24 family FLOOR 變體（FCX-015 首次驗證於 BB Squeeze
Breakout 框架，min(A,B) 0.64→1.43 +123%）。COPX-015 為 repo 首次將 FLOOR
變體跨資產移植至商品/礦業 ETF 同框架，假說 COPX 殘餘 SL/EX 同樣集中於
low-VIX calm regime。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_015_vix_bands_breakout.config import COPX015Config

logger = logging.getLogger(__name__)


class COPX015VixBandsBreakoutDetector(BaseSignalDetector):
    """COPX-015 訊號偵測器"""

    def __init__(self, config: COPX015Config):
        self.config = config

    def _fetch_external(self, ticker: str, start_date: str) -> pd.DataFrame | None:
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
        df = df.copy()

        # === Bollinger Bands（同 COPX-011）===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 COPX-011）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime BOX（同 COPX-011 Att3，lesson #22 + COPX 新發現）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === ^VIX regime gate（COPX-015 核心新增，lesson #24 family FLOOR）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，^VIX 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        regime_ratio = df["SMA_Regime_Short"] / df["SMA_Regime_Long"]
        cond_regime_floor = regime_ratio >= self.config.sma_regime_ratio_min
        cond_regime_cap = regime_ratio <= self.config.sma_regime_ratio_max

        mode = self.config.vix_filter_mode
        vix = df["VIX_Close"]
        low = self.config.vix_low_threshold
        high = self.config.vix_high_threshold
        if mode == "bands_exclude_mid":
            cond_vix = (vix <= low) | (vix > high)
        elif mode == "floor":
            cond_vix = vix > low
        elif mode == "cap":
            cond_vix = vix <= high
        elif mode == "bands_keep_mid":
            cond_vix = (vix > low) & (vix <= high)
        elif mode == "off":
            cond_vix = pd.Series(True, index=df.index)
        else:
            raise ValueError(f"unknown vix_filter_mode: {mode}")

        signal = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_floor
            & cond_regime_cap
            & cond_vix
        )

        df["Signal"] = signal.fillna(False)

        # 冷卻期
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
                "COPX-015: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-015: Detected %d VIX-filtered breakout signals",
            signal_count,
        )
        return df
